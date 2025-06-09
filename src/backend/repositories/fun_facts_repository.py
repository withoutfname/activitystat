import sys
import os
from datetime import datetime, timedelta

# Добавляем корень проекта в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from src.backend.database import Database

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

if __name__ == "__main__":
    try:
        # Подключение к базе данных
        print("[DEBUG] Initializing database connection...")
        db = Database(dbname="activitydb", user="postgres", password="pass", host="localhost", port="5432")
        print("[DEBUG] Database connection established")
        repo = FunFactsRepository(db)

        # Тестируем для 2025 года
        year = 2025
        print(f"\nTesting FunFactsRepository for year {year}:\n")

        # Тест распределения по платформам
        print("Testing get_platform_distribution...")
        platform_dist = repo.get_platform_distribution(year)
        if platform_dist:
            print(f"Platform distribution:")
            print(f"Xbox: {platform_dist['xbox']}%")
            print(f"Steam: {platform_dist['steam']}%")
            print(f"Other: {platform_dist['other']}%")
        else:
            print("No platform distribution data found")

        # Тест игр, в которые играли один день
        print("\nTesting get_games_played_one_day...")
        one_day_games, game_count = repo.get_games_played_one_day(year)
        print(f"Games played only one day (Total: {game_count}):")
        if one_day_games:
            for i, game in enumerate(one_day_games, 1):
                print(f"{i}. {game}")
        else:
            print("No games played only one day")

    except Exception as e:
        print(f"[DEBUG] Error in main: {e}")
    finally:
        print("[DEBUG] Closing database connection...")
        db.close()
