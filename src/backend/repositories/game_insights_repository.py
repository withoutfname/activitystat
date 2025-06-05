class GameInsightsRepository:
    def __init__(self, db):
        self.db = db

    def get_game_of_the_year(self, year):
        """Возвращает игру года по общему времени игры"""
        query = """
        SELECT
            a.alias,
            SUM(EXTRACT(EPOCH FROM (s.end_time - s.start_time))) / 3600 as hours
        FROM activity_sessions s
        JOIN apps a ON s.app_id = a.id
        WHERE EXTRACT(YEAR FROM s.start_time) = %s
          AND s.end_time IS NOT NULL
        GROUP BY a.alias
        ORDER BY hours DESC
        LIMIT 1
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        return {"game": result[0], "hours": round(result[1], 2)} if result else None

    def get_top3_games_percentage(self, year):
        """Возвращает процент времени в топ-3 играх"""
        # Сначала получаем общее время игры за год
        total_query = """
        SELECT SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM start_time) = %s
          AND end_time IS NOT NULL
        """
        self.db.cursor.execute(total_query, (year,))
        total_hours = self.db.cursor.fetchone()[0] or 0

        # Затем получаем топ-3 игр
        top3_query = """
        SELECT
            a.alias,
            SUM(EXTRACT(EPOCH FROM (s.end_time - s.start_time))) / 3600 as hours
        FROM activity_sessions s
        JOIN apps a ON s.app_id = a.id
        WHERE EXTRACT(YEAR FROM s.start_time) = %s
          AND s.end_time IS NOT NULL
        GROUP BY a.alias
        ORDER BY hours DESC
        LIMIT 3
        """
        self.db.cursor.execute(top3_query, (year,))
        top3 = self.db.cursor.fetchall()

        if not top3 or total_hours == 0:
            return {"percentage": 0, "games": []}

        top3_hours = sum(row[1] for row in top3)
        percentage = round((top3_hours / total_hours) * 100, 2)
        games = [{"game": row[0], "hours": round(row[1], 2)} for row in top3]

        return {
            "percentage": percentage,
            "games": games
        }

    def get_new_releases_percentage(self, year):
        """Возвращает процент времени в новинках указанного года и список игр"""
        # Общее время игры за год
        total_query = """
        SELECT SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM start_time) = %s
          AND end_time IS NOT NULL
        """
        self.db.cursor.execute(total_query, (year,))
        total_hours = self.db.cursor.fetchone()[0] or 0

        # Время в новинках года и список игр
        new_query = """
        SELECT
            SUM(EXTRACT(EPOCH FROM (s.end_time - s.start_time))) / 3600 as new_hours,
            a.alias
        FROM activity_sessions s
        JOIN game_metadata gm ON s.app_id = gm.app_id
        JOIN apps a ON s.app_id = a.id
        WHERE EXTRACT(YEAR FROM s.start_time) = %s
          AND s.end_time IS NOT NULL
          AND gm.year = %s
        GROUP BY a.alias
        """
        self.db.cursor.execute(new_query, (year, year))
        new_data = self.db.cursor.fetchall()

        if total_hours == 0:
            return {"percentage": 0, "games": []}

        new_hours = sum(row[0] for row in new_data) if new_data else 0
        percentage = round((new_hours / total_hours) * 100, 2)
        games = [{"game": row[1], "hours": round(row[0], 2)} for row in new_data] if new_data else []

        return {
            "percentage": percentage,
            "games": games
        }

    def get_unique_games_count(self, year):
        """Возвращает количество уникальных игр за год"""
        query = """
        SELECT COUNT(DISTINCT app_id)
        FROM activity_sessions
        WHERE EXTRACT(YEAR FROM start_time) = %s
          AND end_time IS NOT NULL
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        return result[0] if result else 0
