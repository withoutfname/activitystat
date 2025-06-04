
from datetime import datetime, timedelta
import pytz
import psycopg2
from psycopg2 import Error
class Database:
    def __init__(self, dbname="activitydb", user="postgres", password="pass", host="localhost", port="5432"):
        self.connection = None
        self.cursor = None
        try:
            self.connection = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.connection.autocommit = True  # Включаем автокоммит
            self.cursor = self.connection.cursor()
            print("Database connection successful")
        except Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed")


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
                EXTRACT(DOW FROM s.start_time AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Yekaterinburg') as day_of_week,
                SUM(EXTRACT(EPOCH FROM (end_time - start_time))) as total_duration
            FROM activity_sessions s
            WHERE s.end_time IS NOT NULL
            AND s.start_time >= %s
            AND s.start_time <= %s
            GROUP BY EXTRACT(DOW FROM s.start_time AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Yekaterinburg')
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

    @staticmethod
    def main():
        """Тестовый метод для проверки работы репозитория"""
        try:
            db = Database()
            repo = DayOfWeekRepository(db)

            # Получаем статистику за последние 30 дней
            start_days = 200
            end_days = 0
            stats = repo.get_playtime_by_day_of_week(start_days, end_days)

            # Названия дней недели
            days = ["Воскресенье", "Понедельник", "Вторник", "Среда",
                   "Четверг", "Пятница", "Суббота"]

            print("\n=== Статистика по дням недели за последние 30 дней ===")
            for i, hours in enumerate(stats):
                print(f"{days[i]}: {hours:.2f} часов")

            # Находим самый активный день
            max_hours = max(stats)
            max_day = days[stats.index(max_hours)]
            print(f"\nСамый активный день: {max_day} ({max_hours:.2f} часов)")

        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            if db:
                db.close()

if __name__ == "__main__":
    DayOfWeekRepository.main()
