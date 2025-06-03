from src.backend.database import Database

class MetadataRepository:
    def __init__(self, db):
        self.db = db

    def get_tracking_start_date(self):
        query = "SELECT MIN(start_time) FROM activity_sessions"
        self.db.cursor.execute(query)
        result = self.db.cursor.fetchone()
        return result[0] if result else "Unknown"

    def get_max_interval_days(self):
        query = """
            SELECT EXTRACT(DAY FROM (CURRENT_DATE - MIN(start_time))) + 2 
            FROM activity_sessions
        """
        self.db.cursor.execute(query)
        result = self.db.cursor.fetchone()
        return int(result[0])