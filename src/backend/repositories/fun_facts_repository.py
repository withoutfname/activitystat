class FunFactsRepository:
    def __init__(self, db):
        self.db = db

    def get_platform_distribution(self, year):
        """Возвращает распределение игрового времени по платформам (Xbox, Steam, Other)"""
        query = '''
            SELECT
                SUM(CASE WHEN a.exe_path LIKE '%%Xbox Games%%' THEN EXTRACT(EPOCH FROM (s.end_time - s.start_time)) ELSE 0 END) as xbox_seconds,
                SUM(CASE WHEN a.exe_path LIKE '%%SteamLibrary%%' THEN EXTRACT(EPOCH FROM (s.end_time - s.start_time)) ELSE 0 END) as steam_seconds,
                SUM(CASE WHEN a.exe_path NOT LIKE '%%Xbox Games%%' AND a.exe_path NOT LIKE '%%SteamLibrary%%' THEN EXTRACT(EPOCH FROM (s.end_time - s.start_time)) ELSE 0 END) as other_seconds,
                SUM(EXTRACT(EPOCH FROM (s.end_time - s.start_time))) as total_seconds
            FROM activity_sessions s
            JOIN apps a ON s.app_id = a.id
            WHERE EXTRACT(YEAR FROM s.start_time) = %s
            AND s.end_time IS NOT NULL;
        '''

        try:
            self.db.cursor.execute(query, (year,))
            result = self.db.cursor.fetchone()

            if not result or not result[3]:
                return None

            xbox_seconds, steam_seconds, other_seconds, total_seconds = result

            return {
                'xbox': round((xbox_seconds / total_seconds) * 100, 1),
                'steam': round((steam_seconds / total_seconds) * 100, 1),
                'other': round((other_seconds / total_seconds) * 100, 1)
            }
        except Exception as e:
            print(f"[DEBUG] Error in get_platform_distribution: {e}")
            return None

    def get_games_played_one_day(self, year):
        """Возвращает список игр и их количество, в которые играли только один день в указанном году"""
        query = '''
            SELECT a.alias, COUNT(*) as play_count
            FROM apps a
            JOIN (
                SELECT app_id
                FROM activity_sessions
                WHERE EXTRACT(YEAR FROM start_time) = %s
                GROUP BY app_id
                HAVING COUNT(DISTINCT DATE(start_time)) = 1
            ) s ON a.id = s.app_id
            GROUP BY a.alias;
        '''

        try:
            self.db.cursor.execute(query, (year,))
            results = self.db.cursor.fetchall()

            if not results:
                return [], 0

            games = [row[0] for row in results]
            count = len(games)

            return games, count
        except Exception as e:
            print(f"[DEBUG] Error in get_games_played_one_day: {e}")
            return [], 0
