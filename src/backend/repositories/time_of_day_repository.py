from src.backend.database import Database
from datetime import datetime, timedelta
import pytz

class TimeOfDayRepository:
    def __init__(self, db):
        self.db = db
        self.timezone = pytz.timezone("Asia/Yekaterinburg")  # UTC+5 для Уфы/Екатеринбурга

    def get_playtime_by_time_of_day(self, start_days, end_days):
        # Получаем текущую дату и время в заданной таймзоне
        current_date = datetime.now(self.timezone)

        # Формируем интервал дат
        start, end = max(start_days, end_days), min(start_days, end_days)
        start_date = current_date - timedelta(days=start)
        end_date = current_date - timedelta(days=end)

        # Запрос: получаем сессии с временем начала и длительностью
        query = """
            SELECT 
                s.start_time AT TIME ZONE 'Asia/Yekaterinburg' as start_time,
                EXTRACT(EPOCH FROM (end_time - start_time)) as duration
            FROM activity_sessions s
            JOIN apps a ON s.app_id = a.id
            WHERE s.end_time IS NOT NULL
            AND s.start_time >= %s
            AND s.start_time <= %s
            ORDER BY s.start_time
        """
        self.db.cursor.execute(query, (start_date, end_date))
        results = self.db.cursor.fetchall()

        # Инициализируем словарь для хранения времени
        playtime_by_time_of_day = {
            "Morning": 0.0,
            "Afternoon": 0.0,
            "Evening": 0.0,
            "Night": 0.0
        }

        # Определяем интервалы времени суток
        for row in results:
            start_time = row[0]  # Время начала сессии
            duration_seconds = float(row[1])  # Длительность в секундах

            # Получаем час начала сессии (0-23)
            hour = start_time.hour

            # Присваиваем сессию к интервалу
            if 6 <= hour < 12:
                interval = "Morning"
            elif 12 <= hour < 18:
                interval = "Afternoon"
            elif 18 <= hour or hour < 0:  # 18:00-00:00
                interval = "Evening"
            else:  # 00:00-06:00
                interval = "Night"

            # Добавляем длительность (в часах)
            duration_hours = duration_seconds / 3600.0
            playtime_by_time_of_day[interval] += duration_hours

        return playtime_by_time_of_day