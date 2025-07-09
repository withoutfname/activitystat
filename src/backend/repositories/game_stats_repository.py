from datetime import datetime

class GameStatsRepository:
    def __init__(self, db):
        self.db = db


    def get_unique_years(self):
        try:
            # Используем cursor из объекта db для выполнения запроса
            cursor = self.db.cursor
            query = """
                SELECT DISTINCT EXTRACT(YEAR FROM start_time) AS year
                FROM activity_sessions
                WHERE start_time IS NOT NULL
                ORDER BY year DESC
            """
            cursor.execute(query)
            result = cursor.fetchall()
            return [int(row[0]) for row in result if row[0] is not None]  # Приводим к int и фильтруем None
        except Exception as e:
            print(f"Error executing query: {e}")
            return []  # Возвращаем пустой список в случае ошибки

    '''
    def get_unique_years(self):
        try:
            # Используем cursor из объекта db для выполнения запроса
            cursor = self.db.cursor
            query = "SELECT DISTINCT year FROM game_metadata WHERE year IS NOT NULL ORDER BY year DESC"
            cursor.execute(query)
            result = cursor.fetchall()
            return [row[0] for row in result if row[0]]  # Возвращаем список уникальных годов
        except Exception as e:
            print(f"Error executing query: {e}")
            return []  # Возвращаем пустой список в случае ошибки

        '''





    def get_total_playtime_for_year(self, year):
        """Общее время игры в указанном году (в часах)"""
        query = """
        SELECT SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM start_time) = %s AND end_time IS NOT NULL
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        return round(result[0], 2) if result and result[0] else 0.0

    def get_percentage_of_yearly_playtime(self, year):
        """Процент времени игры в году от общего времени за всё время"""
        total_query = """
        SELECT SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600
        FROM activity_sessions
        WHERE end_time IS NOT NULL
        """
        yearly_query = """
        SELECT SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM start_time) = %s AND end_time IS NOT NULL
        """

        self.db.cursor.execute(total_query)
        total_hours = self.db.cursor.fetchone()[0] or 0

        self.db.cursor.execute(yearly_query, (year,))
        yearly_hours = self.db.cursor.fetchone()[0] or 0

        if total_hours == 0:
            return 0.0
        return round((yearly_hours / total_hours) * 100, 2)

    def get_session_count_for_year(self, year):
        """Количество игровых сессий в году"""
        query = """
        SELECT COUNT(*)
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM start_time) = %s AND end_time IS NOT NULL
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        return result[0] if result else 0

    def get_avg_session_duration_for_year(self, year):
        """Средняя длительность сессии в году (в часах), исключая сессии < 30 минут"""
        query = """
        SELECT AVG(EXTRACT(EPOCH FROM (end_time - start_time)) / 3600)
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM start_time) = %s
          AND end_time IS NOT NULL
          AND EXTRACT(EPOCH FROM (end_time - start_time)) >= 1800
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        return round(result[0], 2) if result and result[0] else 0.0

    def get_active_days_percentage_for_year(self, year):
        """Процент дней с игровой активностью в году"""
        days_in_year = 366 if (year % 400 == 0 or (year % 100 != 0 and year % 4 == 0)) else 365

        query = """
        SELECT COUNT(DISTINCT DATE(start_time))
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM start_time) = %s
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        active_days = result[0] if result else 0

        return round((active_days / days_in_year) * 100, 2)

    def get_most_active_month_for_year(self, year):
        """Самый активный месяц в году (название месяца и часы)"""
        query = """
        SELECT
            EXTRACT(MONTH FROM start_time) as month,
            SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600 as hours
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM start_time) = %s AND end_time IS NOT NULL
        GROUP BY month
        ORDER BY hours DESC
        LIMIT 1
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        if not result:
            return None

        month_num = int(result[0])
        month_name = datetime(2000, month_num, 1).strftime('%B')  # Теперь datetime используется правильно
        return {"month": month_name, "hours": round(result[1], 2)}

    def get_least_active_month_for_year(self, year):
        """Самый пассивный месяц в году (название месяца и часы)"""
        query = """
        SELECT
            EXTRACT(MONTH FROM start_time) as month,
            SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600 as hours
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM start_time) = %s AND end_time IS NOT NULL
        GROUP BY month
        ORDER BY hours ASC
        LIMIT 1
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        if not result:
            return None

        month_num = int(result[0])
        month_name = datetime(2000, month_num, 1).strftime('%B')
        return {"month": month_name, "hours": round(result[1], 2)}

    def get_most_active_day_of_week_for_year(self, year):
        """Самый активный день недели в году (название дня и часы)"""
        query = """
        SELECT
            EXTRACT(DOW FROM (start_time AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Yekaterinburg')) as day_of_week,
            SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600 as hours
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM (start_time AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Yekaterinburg')) = %s
          AND end_time IS NOT NULL
        GROUP BY day_of_week
        ORDER BY hours DESC
        LIMIT 1
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        if not result:
            return None

        day_num = int(result[0])
        days = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        return {"day": days[day_num], "hours": round(result[1], 2)}

    def get_most_active_time_of_day_for_year(self, year):
        """Самое активное время суток в году (период и часы)"""
        query = """
        SELECT
            CASE
                WHEN EXTRACT(HOUR FROM start_time) BETWEEN 6 AND 11 THEN 'Morning'
                WHEN EXTRACT(HOUR FROM start_time) BETWEEN 12 AND 17 THEN 'Afternoon'
                WHEN EXTRACT(HOUR FROM start_time) BETWEEN 18 AND 23 THEN 'Evening'
                ELSE 'Night'
            END as time_period,
            SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600 as hours
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM start_time) = %s AND end_time IS NOT NULL
        GROUP BY time_period
        ORDER BY hours DESC
        LIMIT 1
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        return {"time_period": result[0], "hours": round(result[1], 2)} if result else None

    def get_longest_gaming_day_for_year(self, year):
        """Самый длинный игровой день в году (дата и часы)"""
        query = """
        SELECT
            DATE(start_time) as day,
            SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600 as hours
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM start_time) = %s AND end_time IS NOT NULL
        GROUP BY day
        ORDER BY hours DESC
        LIMIT 1
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        if not result:
            return None

        date_str = result[0].strftime('%d %B')
        return {"date": date_str, "hours": round(result[1], 2)}
