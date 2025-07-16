import sys
import os

# Добавляем корень проекта в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from src.backend.database.database import Database

class ReleaseYearStatsRepository:
    def __init__(self, db):
        self.db = db

    def get_playtime_by_release_year(self, year):
        """Возвращает процентное распределение игрового времени по годам выпуска игр"""
        query = '''
            SELECT g.year, SUM(EXTRACT(EPOCH FROM (s.end_time - s.start_time))/3600) as total_hours
            FROM game_metadata g
            JOIN activity_sessions s ON g.app_id = s.app_id
            WHERE EXTRACT(YEAR FROM s.start_time) = %s
            AND g.year IS NOT NULL
            AND s.end_time IS NOT NULL
            GROUP BY g.year;
        '''
        try:
            self.db.cursor.execute(query, (year,))
            results = self.db.cursor.fetchall()
            if not results:
                print(f"[DEBUG] No playtime data found for year {year}")
                return {'selected_year': 'N/A', 'previous_year': 'N/A', 'older_years': 'N/A'}

            total_hours = sum(row[1] for row in results if row[1] is not None)
            if total_hours == 0:
                print(f"[DEBUG] Total playtime is zero for year {year}")
                return {'selected_year': 'N/A', 'previous_year': 'N/A', 'older_years': 'N/A'}

            selected_year_hours = 0
            previous_year_hours = 0
            older_years_hours = 0

            for release_year, hours in results:
                if release_year is not None and hours is not None:
                    if release_year == year:
                        selected_year_hours += hours
                    elif release_year == year - 1:
                        previous_year_hours += hours
                    else:
                        older_years_hours += hours

            return {
                'selected_year': round((selected_year_hours / total_hours) * 100, 1),
                'previous_year': round((previous_year_hours / total_hours) * 100, 1),
                'older_years': round((older_years_hours / total_hours) * 100, 1)
            }
        except Exception as e:
            print(f"[DEBUG] Error executing query in get_playtime_by_release_year: {e}")
            return {'selected_year': 'N/A', 'previous_year': 'N/A', 'older_years': 'N/A'}

    def get_oldest_game_played(self, year):
        """Возвращает самую старую игру, в которую играли в указанном году"""
        query = '''
            SELECT a.alias, g.year
            FROM game_metadata g
            JOIN activity_sessions s ON g.app_id = s.app_id
            JOIN apps a ON g.app_id = a.id
            WHERE EXTRACT(YEAR FROM s.start_time) = %s
            AND g.year IS NOT NULL
            AND s.end_time IS NOT NULL
            ORDER BY g.year ASC
            LIMIT 1;
        '''
        try:
            self.db.cursor.execute(query, (year,))
            result = self.db.cursor.fetchone()

            # Возвращаем None если нет результатов
            if not result:
                return None

            alias, release_year = result
            return {'alias': alias, 'year': release_year}
        except Exception as e:
            print(f"[ERROR] Error in get_oldest_game_played: {e}")
            return None

if __name__ == "__main__":
    try:
        # Подключение к базе данных
        print("[DEBUG] Initializing database connection...")
        db = Database(dbname="activitydb", user="postgres", password="pass", host="localhost", port="5432")
        print("[DEBUG] Database connection established")
        repo = ReleaseYearStatsRepository(db)

        # Тестируем для 2024 года
        year = 2024
        print(f"\nTesting ReleaseYearStatsRepository for year {year}:\n")

        # Тест get_playtime_by_release_year
        print("Testing get_playtime_by_release_year...")
        playtime_dist = repo.get_playtime_by_release_year(year)
        print("Playtime by release year:")
        print(f"{year}: {playtime_dist['selected_year']}%")
        print(f"{year-1}: {playtime_dist['previous_year']}%")
        print(f"Older: {playtime_dist['older_years']}%")

        # Тест get_oldest_game_played
        print("\nTesting get_oldest_game_played...")
        oldest_game = repo.get_oldest_game_played(year)
        print("Oldest game played:")
        print(f"{oldest_game['alias']} ({oldest_game['year']})" if oldest_game else "N/A")

    except Exception as e:
        print(f"[DEBUG] Error in main: {e}")
    finally:
        print("[DEBUG] Closing database connection...")
        db.close()
