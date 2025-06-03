from src.backend.database import Database

class MaxSessionRepository:
    def __init__(self, db):
        self.db = db

    def get_max_session_duration(self, start_days=None, end_days=None):
        query = """
            SELECT EXTRACT(EPOCH FROM (end_time - start_time)) as duration, 
                   a.alias, 
                   DATE(start_time) as session_date
            FROM activity_sessions s
            JOIN apps a ON s.app_id = a.id
            WHERE s.end_time IS NOT NULL
        """
        params = []
        if start_days is not None and end_days is not None:
            start, end = max(start_days, end_days), min(start_days, end_days)
            query += " AND s.start_time >= CURRENT_DATE - INTERVAL %s AND s.start_time <= CURRENT_DATE - INTERVAL %s"
            params.extend([f"{start} days", f"{end} days"])
        elif start_days is not None:
            query += " AND s.start_time >= CURRENT_DATE - INTERVAL %s"
            params.append(f"{start_days} days")

        query += " ORDER BY duration DESC LIMIT 1"
        self.db.cursor.execute(query, params)
        result = self.db.cursor.fetchone()
        if result and result[0] is not None:
            return (float(result[0]) / 3600.0, result[1], result[2].strftime('%d-%m-%Y'))
        return (0.0, '', '')

    def get_max_daily_game_session(self, start_days=None, end_days=None):
        query = """
            SELECT 
                SUM(EXTRACT(EPOCH FROM (end_time - start_time))) as total_duration,
                DATE(s.start_time) as session_date,
                a.alias,
                COUNT(*) as session_count
            FROM activity_sessions s
            JOIN apps a ON s.app_id = a.id
            WHERE s.end_time IS NOT NULL
        """
        params = []
        if start_days is not None and end_days is not None:
            start, end = max(start_days, end_days), min(start_days, end_days)
            query += " AND s.start_time >= CURRENT_DATE - INTERVAL %s AND s.start_time <= CURRENT_DATE - INTERVAL %s"
            params.extend([f"{start} days", f"{end} days"])
        elif start_days is not None:
            query += " AND s.start_time >= CURRENT_DATE - INTERVAL %s"
            params.append(f"{start_days} days")

        query += """
            GROUP BY DATE(s.start_time), a.id, a.name
            ORDER BY total_duration DESC
            LIMIT 1
        """
        self.db.cursor.execute(query, params)
        result = self.db.cursor.fetchone()
        if result and result[0] is not None:
            return (float(result[0]) / 3600.0, result[1].strftime('%d-%m-%Y'), result[2], int(result[3]))
        return (0.0, '', '', 0)


    def get_max_daily_total_duration(self, start_days=None, end_days=None):
        # Первый запрос: найти день с максимальной длительностью
        query_max_day = """
            SELECT DATE(start_time) as max_date, 
                   SUM(EXTRACT(EPOCH FROM (end_time - start_time))) as total_duration
            FROM activity_sessions
            WHERE end_time IS NOT NULL
        """
        params = []
        if start_days is not None and end_days is not None:
            start, end = max(start_days, end_days), min(start_days, end_days)
            query_max_day += " AND start_time >= CURRENT_DATE - INTERVAL %s AND start_time <= CURRENT_DATE - INTERVAL %s"
            params.extend([f"{start} days", f"{end} days"])
        elif start_days is not None:
            query_max_day += " AND start_time >= CURRENT_DATE - INTERVAL %s"
            params.append(f"{start_days} days")

        query_max_day += " GROUP BY DATE(start_time) ORDER BY total_duration DESC LIMIT 1"
        self.db.cursor.execute(query_max_day, params)
        result = self.db.cursor.fetchone()

        if result and result[1] is not None:
            max_date = result[0]
            max_duration = float(result[1]) / 3600.0

            # Второй запрос: получить игры и их длительности для этого дня
            query_games = """
                SELECT a.alias, 
                       ROUND(SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600.0, 1) as duration
                FROM activity_sessions s
                JOIN apps a ON s.app_id = a.id
                WHERE s.end_time IS NOT NULL AND DATE(s.start_time) = %s
                GROUP BY a.id, a.alias
                ORDER BY duration DESC
            """
            self.db.cursor.execute(query_games, [max_date])
            games = self.db.cursor.fetchall()
            game_details = ", ".join(f"{game[0]}: {game[1]}h" for game in games) if games else "No games"
            return (max_duration, max_date.strftime('%d-%m-%Y'), game_details)
        return (0.0, '', '')