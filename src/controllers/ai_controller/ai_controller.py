# src/controllers/ai_controller/ai_controller.py
import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from PySide6.QtCore import QObject, Slot, Signal, Property
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import Dataset, DataLoader
from sqlalchemy import create_engine

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=1):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

class TimeSeriesDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class AiController(QObject):
    def __init__(self, stats_service):
        super().__init__()
        self._stats_service = stats_service
        self._forecast_data = []
        self._historical_data = []
        self._plot_path = ""

        # Initialize model parameters
        self.sequence_length = 7
        self.forecast_days = 30
        self.num_epochs = 50

    forecastDataChanged = Signal()
    historicalDataChanged = Signal()
    plotPathChanged = Signal()
    trainingProgressChanged = Signal(float, str)
    forecastCompleted = Signal(bool, str)

    @Property(list, notify=forecastDataChanged)
    def forecastData(self):
        return self._forecast_data

    @Property(list, notify=historicalDataChanged)
    def historicalData(self):
        return self._historical_data

    @Property(str, notify=plotPathChanged)
    def plotPath(self):
        return self._plot_path

    @Slot()
    def generateForecast(self):
        try:
            self.trainingProgressChanged.emit(0, "Loading data...")

            # Get data from database
            db_params = {
                'dbname': 'activitydb',
                'user': 'postgres',
                'password': 'pass',
                'host': 'localhost',
                'port': '5432'
            }

            db_string = f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
            engine = create_engine(db_string)

            query = """
            SELECT start_time, end_time
            FROM public.activity_sessions
            WHERE end_time IS NOT NULL;
            """

            df = pd.read_sql(query, engine)
            engine.dispose()

            self.trainingProgressChanged.emit(0.1, "Processing data...")

            # Process data
            df['start_time'] = pd.to_datetime(df['start_time'])
            df['end_time'] = pd.to_datetime(df['end_time'])
            df['duration_hours'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600
            df['date'] = df['start_time'].dt.date

            daily_totals = df.groupby('date')['duration_hours'].sum().reset_index()
            first_date = pd.to_datetime(daily_totals['date'].min())
            current_date = pd.to_datetime(datetime.now().date())

            all_dates = pd.date_range(start=first_date, end=current_date, freq='D')
            daily_totals_indexed = pd.DataFrame({'date': all_dates})
            daily_totals['date'] = pd.to_datetime(daily_totals['date'])
            daily_totals_indexed = daily_totals_indexed.merge(daily_totals, on='date', how='left').fillna({'duration_hours': 0})
            daily_totals_indexed['cumulative_hours'] = daily_totals_indexed['duration_hours'].cumsum()

            self.trainingProgressChanged.emit(0.2, "Preparing model...")

            # Prepare model
            scaler = MinMaxScaler()
            daily_totals_indexed['duration_scaled'] = scaler.fit_transform(daily_totals_indexed[['duration_hours']])

            X, y = self._create_sequences(daily_totals_indexed['duration_scaled'].values, self.sequence_length)
            X = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)
            y = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)

            dataset = TimeSeriesDataset(X, y)
            dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

            model = LSTMModel()
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

            self.trainingProgressChanged.emit(0.3, "Training model...")

            # Train model
            for epoch in range(self.num_epochs):
                for X_batch, y_batch in dataloader:
                    optimizer.zero_grad()
                    y_pred = model(X_batch)
                    loss = criterion(y_pred, y_batch)
                    loss.backward()
                    optimizer.step()

                progress = 0.3 + 0.5 * (epoch + 1) / self.num_epochs
                self.trainingProgressChanged.emit(progress, f"Training epoch {epoch+1}/{self.num_epochs}")

            self.trainingProgressChanged.emit(0.8, "Generating forecast...")

            # Generate forecast
            last_sequence = daily_totals_indexed['duration_scaled'].values[-self.sequence_length:]
            last_sequence = torch.tensor(last_sequence, dtype=torch.float32).reshape(1, self.sequence_length, 1)

            model.eval()
            forecasted = []
            with torch.no_grad():
                current_sequence = last_sequence
                for _ in range(self.forecast_days):
                    pred = model(current_sequence)
                    forecasted.append(pred.item())
                    pred = pred.reshape(1, 1, 1)
                    current_sequence = torch.cat((current_sequence[:, 1:, :], pred), dim=1)

            forecasted = scaler.inverse_transform(np.array(forecasted).reshape(-1, 1)).flatten()

            future_dates = pd.date_range(start=current_date + pd.Timedelta(days=1), periods=self.forecast_days, freq='D')
            forecast_df = pd.DataFrame({
                'date': future_dates,
                'duration_hours': forecasted
            })
            forecast_df['cumulative_hours'] = daily_totals_indexed['cumulative_hours'].iloc[-1] + forecast_df['duration_hours'].cumsum()

            # Prepare data for QML
            self._historical_data = [{
                'date': str(row['date']),
                'hours': row['duration_hours'],
                'cumulative': row['cumulative_hours']
            } for _, row in daily_totals_indexed.iterrows()]

            self._forecast_data = [{
                'date': str(row['date']),
                'hours': row['duration_hours'],
                'cumulative': row['cumulative_hours']
            } for _, row in forecast_df.iterrows()]

            self.historicalDataChanged.emit()
            self.forecastDataChanged.emit()

            # Generate plot
            self._generate_plot(daily_totals_indexed, forecast_df)

            self.trainingProgressChanged.emit(1.0, "Forecast completed")
            self.forecastCompleted.emit(True, "Forecast generated successfully")

        except Exception as e:
            self.forecastCompleted.emit(False, f"Error: {str(e)}")
            self.trainingProgressChanged.emit(0.0, f"Error: {str(e)}")

    def _create_sequences(self, data, seq_length):
        xs, ys = [], []
        for i in range(len(data) - seq_length):
            x = data[i:i + seq_length]
            y = data[i + seq_length]
            xs.append(x)
            ys.append(y)
        return np.array(xs), np.array(ys)

    def _generate_plot(self, historical, forecast):
        try:
            import matplotlib.pyplot as plt
            from datetime import datetime

            plt.figure(figsize=(10, 6))
            plt.plot(historical['date'], historical['cumulative_hours'],
                    label='Historical', marker='o')
            plt.plot(forecast['date'], forecast['cumulative_hours'],
                    label='Forecast', linestyle='--', marker='o')

            plt.title('Game Time Forecast')
            plt.xlabel('Date')
            plt.ylabel('Cumulative Hours')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()

            # Save plot
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            plot_path = os.path.join(current_dir, "assets", "forecast_plot.png")
            os.makedirs(os.path.dirname(plot_path), exist_ok=True)
            plt.savefig(plot_path)
            plt.close()

            self._plot_path = plot_path
            self.plotPathChanged.emit()

        except Exception as e:
            print(f"Error generating plot: {e}")
