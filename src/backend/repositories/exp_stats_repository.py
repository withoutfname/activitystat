class ExpStatsRepository:
    def __init__(self, db):
        self.db = db

    def get_overplayed_time_percentage_in_year(self, year):
        """Возвращает процент и количество сессий, где продолжительность > 3 часов в указанном году"""
        query = """
        WITH overplayed AS (
            SELECT COUNT(*) as overplayed_count
            FROM activity_sessions s
            JOIN apps a ON s.app_id = a.id
            WHERE EXTRACT(YEAR FROM s.start_time) = %s
            AND s.end_time IS NOT NULL
            AND EXTRACT(EPOCH FROM (s.end_time - s.start_time)) > 10800 -- 3 часа в секундах
        ),
        total_sessions AS (
            SELECT COUNT(*) as total_count
            FROM activity_sessions s
            WHERE EXTRACT(YEAR FROM s.start_time) = %s
            AND s.end_time IS NOT NULL
        )
        SELECT
            COALESCE((SELECT overplayed_count FROM overplayed), 0) as overplayed_count,
            COALESCE((SELECT total_count FROM total_sessions), 0) as total_count,
            CASE
                WHEN (SELECT total_count FROM total_sessions) = 0 THEN 0
                ELSE ROUND((SELECT overplayed_count FROM overplayed)::numeric / (SELECT total_count FROM total_sessions) * 100, 2)
            END as percentage;
        """
        try:
            self.db.cursor.execute(query, (year, year))
            result = self.db.cursor.fetchone()
            if not result:
                return {'overplayed_count': 0, 'total_count': 0, 'percentage': 0.0}
            overplayed_count, total_count, percentage = result
            return {
                'overplayed_count': overplayed_count,
                'total_count': total_count,
                'percentage': percentage
            }
        except Exception as e:
            print(f"[DEBUG] Error in get_overplayed_time_percentage_in_year: {e}")
            return {'overplayed_count': 0, 'total_count': 0, 'percentage': 0.0}
