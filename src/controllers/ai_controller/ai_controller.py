from PySide6.QtCore import QObject, Signal, QThread, Slot
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from datetime import datetime, timedelta

class TimeSeriesDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=1):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

class ForecastWorker(QThread):
    finished = Signal(list, list, str)  # historical_data, forecast_data, error

    def __init__(self, stats_service):
        super().__init__()
        self.stats_service = stats_service

    def run(self):
        try:
            # Получаем начальную дату отслеживания
            start_date = self.stats_service.get_tracking_start_date()
            if not start_date or start_date == "Unknown":
                self.finished.emit([], [], "Нет данных о начале отслеживания")
                return

            start_date = pd.to_datetime(start_date)
            current_date = pd.to_datetime(datetime.now().date())

            # Получаем данные по дням
            all_dates = pd.date_range(start=start_date, end=current_date, freq='D')
            daily_hours = []
            for date in all_dates:
                total_hours = self.stats_service.get_simp_total_playtime(
                    start_days=(current_date - date).days,
                    end_days=(current_date - date).days
                )
                if total_hours is None:
                    total_hours = 0.0
                daily_hours.append(float(total_hours))

                print(f"Дата: {date}, Часы: {total_hours}")

            # Создаем DataFrame
            daily_totals = pd.DataFrame({
                'date': all_dates,
                'duration_hours': daily_hours
            })
            daily_totals['days_since_start'] = [(d - start_date).days for d in daily_totals['date']]
            daily_totals['cumulative_hours'] = daily_totals['duration_hours'].cumsum()

            # Проверяем, что данные валидны
            if daily_totals['duration_hours'].isna().any() or daily_totals['cumulative_hours'].isna().any():
                self.finished.emit([], [], "Ошибка: В данных есть пропущенные значения")
                return

            # Подготовка данных для LSTM
            sequence_length = 7
            scaler = MinMaxScaler()
            daily_totals['duration_scaled'] = scaler.fit_transform(daily_totals[['duration_hours']])

            # Создание последовательностей
            def create_sequences(data, seq_length):
                xs, ys = [], []
                for i in range(len(data) - seq_length):
                    x = data[i:i + seq_length]
                    y = data[i + seq_length]
                    xs.append(x)
                    ys.append(y)
                return np.array(xs), np.array(ys)

            X, y = create_sequences(daily_totals['duration_scaled'].values, sequence_length)
            if len(X) == 0:
                self.finished.emit([], [], "Недостаточно данных для обучения модели (нужно минимум 7 дней)")
                return

            X = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)
            y = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)

            # Создаем Dataset и DataLoader
            dataset = TimeSeriesDataset(X, y)
            dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

            # Инициализация модели
            model = LSTMModel()
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

            # Обучение модели
            num_epochs = 50
            for epoch in range(num_epochs):
                for X_batch, y_batch in dataloader:
                    optimizer.zero_grad()
                    y_pred = model(X_batch)
                    loss = criterion(y_pred, y_batch)
                    loss.backward()
                    optimizer.step()

            # Прогнозирование на 30 дней
            forecast_days = 30
            future_dates = pd.date_range(start=current_date + timedelta(days=1), periods=forecast_days, freq='D')
            future_days_since_start = [(d - start_date).days for d in future_dates]

            last_sequence = daily_totals['duration_scaled'].values[-sequence_length:]
            last_sequence = torch.tensor(last_sequence, dtype=torch.float32).reshape(1, sequence_length, 1)

            # Прогнозирование
            model.eval()
            forecasted = []
            with torch.no_grad():
                current_sequence = last_sequence
                for _ in range(forecast_days):
                    prev_pred = model(current_sequence)
                    forecasted.append(prev_pred.item())
                    pred = prev_pred.reshape(1, 1, 1)
                    current_sequence = torch.cat((current_sequence[:, 1:, :], pred), dim=1)

            # Обратное масштабирование
            forecasted = scaler.inverse_transform(np.array(forecasted).reshape(-1, 1)).flatten()

            # Создание DataFrame для прогноза
            forecast_df = pd.DataFrame({
                'days_since_start': future_days_since_start,
                'duration_hours': forecasted
            })
            forecast_df['cumulative_hours'] = daily_totals['cumulative_hours'].iloc[-1] + forecast_df['duration_hours'].cumsum()

            # Проверяем прогноз на валидность
            if forecast_df['cumulative_hours'].isna().any():
                self.finished.emit([], [], "Ошибка: Прогноз содержит пропущенные значения")
                return

            # Формируем данные для QML
            historical_data = [
                [float(row['days_since_start']), float(row['cumulative_hours'])]
                for _, row in daily_totals.iterrows()
            ]
            forecast_data = [
                [float(row['days_since_start']), float(row['cumulative_hours'])]
                for _, row in forecast_df.iterrows()
            ]

            self.finished.emit(historical_data, forecast_data, "")

        except Exception as e:
            print(f"Ошибка в ForecastWorker: {str(e)}")
            self.finished.emit([], [], f"Ошибка: {str(e)}")

class AiController(QObject):
    forecastReady = Signal(list, list, str)  # historical_data, forecast_data, error

    def __init__(self, stats_service):
        super().__init__()
        self.stats_service = stats_service
        self.worker = None

    @Slot()
    def generateForecast(self):
        """Запускает прогнозирование в отдельном потоке."""
        if self.worker and self.worker.isRunning():
            return  # Не запускаем, если уже выполняется

        self.worker = ForecastWorker(self.stats_service)
        self.worker.finished.connect(self.onForecastFinished)
        self.worker.start()

    @Slot(list, list, str)
    def onForecastFinished(self, historical_data, forecast_data, error):
        """Обработка завершения прогнозирования."""
        self.forecastReady.emit(historical_data, forecast_data, error)
        self.worker.deleteLater()
        self.worker = None
