

class DayRepository:
    def __init__(self, db):
        self.db = db

    def get_active_days_count(self, start_days=None, end_days=None):
        query = """
            SELECT COUNT(DISTINCT DATE(start_time))
            FROM activity_sessions
            WHERE end_time IS NOT NULL
              AND EXTRACT(EPOCH FROM (end_time - start_time)) >= 1800
        """
        params = []
        if start_days is not None:
            if end_days is not None:
                start, end = max(start_days, end_days), min(start_days, end_days)
                query += " AND start_time >= CURRENT_DATE - INTERVAL %s AND start_time <= CURRENT_DATE - INTERVAL %s"
                params.extend([f"{start} days", f"{end} days"])
            else:
                query += " AND start_time >= CURRENT_DATE - INTERVAL %s"
                params.append(f"{start_days} days")

        self.db.cursor.execute(query, params)
        result = self.db.cursor.fetchone()
        return result[0] if result else 0