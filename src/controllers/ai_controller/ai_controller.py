from PySide6.QtCore import QObject, Signal, QThread, Slot
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.interpolate import CubicSpline
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings

class ForecastWorker(QThread):
    finished = Signal(list, list, str)  # historical_data, forecast_data, error

    def __init__(self, stats_service):
        super().__init__()
        self.stats_service = stats_service



    def run(self):
        try:
            # Отключаем предупреждения statsmodels
            warnings.filterwarnings("ignore", category=Warning)

            # Получаем начальную дату отслеживания
            start_date = self.stats_service.get_tracking_start_date()
            if not start_date or start_date == "Unknown":
                self.finished.emit([], [], "Нет данных о начале отслеживания")
                return

            start_date = pd.to_datetime(start_date)
            current_date = pd.to_datetime(datetime.now().date())

            print(f"Начальная дата: {start_date}, Текущая дата: {current_date}")

            # Получаем данные по дням
            all_dates = pd.date_range(start=start_date, end=current_date, freq='D')
            daily_hours = []

            # Проверяем наличие метода get_daily_simp_playtime
            try:
                daily_data = self.stats_service.get_daily_simp_playtime(start_date, current_date)
                daily_hours = [0.0] * len(all_dates)
                for date, hours in daily_data:
                    date = pd.to_datetime(date)
                    idx = (date - start_date).days
                    if 0 <= idx < len(daily_hours):
                        daily_hours[idx] = float(hours) if hours is not None else 0.0
                print(f"Использован метод get_daily_simp_playtime, получено {len(daily_data)} записей")
            except AttributeError:
                print("Метод get_daily_simp_playtime не найден, используем get_simp_total_playtime")
                for date in all_dates:
                    total_hours = self.stats_service.get_simp_total_playtime(
                        start_days=(current_date - date).days,
                        end_days=(current_date - date).days
                    )
                    if total_hours is None:
                        total_hours = 0.0
                    daily_hours.append(float(total_hours))

            print(f"Получено {len(daily_hours)} дней данных, первые 5 значений: {daily_hours[:5]}")

            # Создаем DataFrame
            daily_totals = pd.DataFrame({
                'date': all_dates,
                'duration_hours': daily_hours
            })
            daily_totals['days_since_start'] = [(d - start_date).days for d in daily_totals['date']]
            daily_totals['cumulative_hours'] = daily_totals['duration_hours'].cumsum()

            print(f"Создан DataFrame с {len(daily_totals)} строками")
            print(f"Последние 5 значений cumulative_hours:\n{daily_totals[['date', 'cumulative_hours']].tail()}")

            # Проверяем, что данные валидны
            if daily_totals['duration_hours'].isna().any() or daily_totals['cumulative_hours'].isna().any():
                error_msg = "Ошибка: В данных есть пропущенные значения"
                print(error_msg)
                self.finished.emit([], [], error_msg)
                return

            # Формируем исторические данные для графика
            historical_data = daily_totals[['days_since_start', 'cumulative_hours']].values.tolist()
            print(f"Сформировано {len(historical_data)} точек исторических данных")

            # Проверяем, достаточно ли данных для прогноза
            if len(daily_totals) < 7:
                error_msg = f"Недостаточно данных для прогноза (только {len(daily_totals)} дней)"
                print(error_msg)
                self.finished.emit(historical_data, [], error_msg)
                return

            # Holt-Winters для предсказания ЕЖЕДНЕВНЫХ значений (не кумулятивных)
            forecast_days = 30
            ts = pd.Series(daily_totals['duration_hours'].values,
                          index=pd.date_range(start=start_date, periods=len(daily_totals), freq='D'))
            print(f"Создан временной ряд с частотой: {ts.index.freq}")

            try:
                model = ExponentialSmoothing(ts, trend='add', seasonal='add', seasonal_periods=7)
                results = model.fit()
                print("Модель Holt-Winters успешно обучена")

                # Прогноз на 30 дней (ежедневных значений)
                daily_forecast = results.forecast(steps=forecast_days)
                print(f"Прогноз ежедневных часов (первые 5): {daily_forecast.head()}")

                # Создаем прогнозные данные для графика (кумулятивные)
                forecast_data = []
                last_day = daily_totals['days_since_start'].iloc[-1]
                last_cumulative = daily_totals['cumulative_hours'].iloc[-1]

                cumulative = last_cumulative
                for i in range(forecast_days):
                    day = last_day + i + 1
                    cumulative += daily_forecast.iloc[i]  # Добавляем прогнозируемое дневное значение
                    forecast_data.append([float(day), float(cumulative)])

                print(f"Прогноз кумулятивных часов на 30-й день: {cumulative:.2f}")
                print(f"Сформирован прогноз на {forecast_days} дней")
                self.finished.emit(historical_data, forecast_data, "")

            except Exception as e:
                error_msg = f"Ошибка при прогнозировании: {str(e)}"
                print(error_msg)
                self.finished.emit(historical_data, [], error_msg)

        except Exception as e:
            error_msg = f"Ошибка в ForecastWorker: {str(e)}"
            print(error_msg)
            self.finished.emit([], [], error_msg)




class AiController(QObject):
    forecastReady = Signal(list, list, str)  # historical_data, forecast_data, error

    def __init__(self, stats_service):
        super().__init__()
        self.stats_service = stats_service
        self.worker = None
        # Запускаем прогнозирование сразу при инициализации
        self.generateForecast()

    @Slot()
    def generateForecast(self):
        """Запускает прогнозирование в отдельном потоке."""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()  # Прерываем предыдущий поток, если он работает

        self.worker = ForecastWorker(self.stats_service)
        self.worker.finished.connect(self.onForecastFinished)
        self.worker.start()

    @Slot(list, list, str)
    def onForecastFinished(self, historical_data, forecast_data, error):
        """Обработка завершения прогнозирования."""
        self.forecastReady.emit(historical_data, forecast_data, error)
        self.worker.deleteLater()
        self.worker = None
