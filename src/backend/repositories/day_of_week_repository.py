from src.backend.database import Database
from datetime import datetime, timedelta
import pytz

class DayOfWeekRepository:
    def __init__(self, db):
        self.db = db
        self.timezone = pytz.timezone("Asia/Yekaterinburg")  # UTC+5 для Уфы/Екатеринбурга

    def get_playtime_by_day_of_week(self, start_days, end_days):
        # Получаем текущую дату и время в заданной таймзоне
        current_date = datetime.now(self.timezone)

        # Формируем интервал дат
        start, end = max(start_days, end_days), min(start_days, end_days)
        start_date = current_date - timedelta(days=start)
        end_date = current_date - timedelta(days=end)

        # Запрос: группируем сессии по дням недели и считаем общее время
        query = """
            SELECT 
                EXTRACT(DOW FROM s.start_time AT TIME ZONE 'Europe/Paris') as day_of_week,
                SUM(EXTRACT(EPOCH FROM (end_time - start_time))) as total_duration
            FROM activity_sessions s
            WHERE s.end_time IS NOT NULL
            AND s.start_time >= %s
            AND s.start_time <= %s
            GROUP BY EXTRACT(DOW FROM s.start_time AT TIME ZONE 'Europe/Paris')
        """
        self.db.cursor.execute(query, (start_date, end_date))
        results = self.db.cursor.fetchall()

        # Инициализируем массив для хранения времени по дням недели (0 - воскресенье, 1 - понедельник, ..., 6 - суббота)
        playtime_by_day = [0.0] * 7

        # Обрабатываем результаты
        for row in results:
            day_of_week = int(row[0])  # День недели (0-6)
            duration = float(row[1]) / 3600.0  # Длительность в часах
            playtime_by_day[day_of_week] = duration

        return playtime_by_day