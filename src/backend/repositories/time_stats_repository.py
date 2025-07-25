class TimeStatsRepository:
    def __init__(self, db):
        self.db = db

    def get_full_total_seconds(self, start_days=None, end_days=None):
        query = """
            SELECT SUM(EXTRACT(EPOCH FROM (end_time - start_time)))
            FROM activity_sessions
            WHERE end_time IS NOT NULL
        """
        params = []
        if start_days is not None:
            if end_days is not None:
                start, end = max(start_days, end_days), min(start_days, end_days)
                query += " AND start_time >= CURRENT_DATE - INTERVAL %s AND start_time < CURRENT_DATE - INTERVAL %s + INTERVAL '1 day'"
                params.extend([f"{start} days", f"{end} days"])
            else:
                query += " AND start_time >= CURRENT_DATE - INTERVAL %s"
                params.append(f"{start_days} days")

        self.db.cursor.execute(query, params)
        total_seconds = self.db.cursor.fetchone()
        return float(total_seconds[0]) if total_seconds and total_seconds[0] is not None else 0.0

    def get_simp_total_seconds(self, start_days=None, end_days=None):
        query = """
            SELECT SUM(EXTRACT(EPOCH FROM (end_time - start_time)))
            FROM activity_sessions
            WHERE end_time IS NOT NULL
              AND EXTRACT(EPOCH FROM (end_time - start_time)) >= 600
        """
        params = []
        if start_days is not None:
            if end_days is not None:
                start, end = max(start_days, end_days), min(start_days, end_days)
                query += " AND start_time >= CURRENT_DATE - INTERVAL %s AND start_time < CURRENT_DATE - INTERVAL %s + INTERVAL '1 day'"
                params.extend([f"{start} days", f"{end} days"])
            else:
                query += " AND start_time >= CURRENT_DATE - INTERVAL %s"
                params.append(f"{start_days} days")

        self.db.cursor.execute(query, params)
        total_seconds = self.db.cursor.fetchone()
        return float(total_seconds[0]) if total_seconds and total_seconds[0] is not None else 0.0
