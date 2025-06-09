import sys
import os

# Добавляем корень проекта в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from src.backend.database import Database

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

if __name__ == "__main__":
    try:
        print("[DEBUG] Initializing database connection...")
        db = Database(dbname="activitydb", user="postgres", password="pass", host="localhost", port="5432")
        print("[DEBUG] Database connection established")
        repo = ExpStatsRepository(db)

        # Тестируем для 2025 года
        year = 2025
        print(f"\nTesting ExpStatsRepository for year {year}:\n")

        # Тест get_overplayed_time_percentage_in_year
        stats = repo.get_overplayed_time_percentage_in_year(year)
        print(f"Overplayed time stats:")
        print(f"Number of overplayed sessions (>3 hours): {stats['overplayed_count']}")
        print(f"Total number of sessions: {stats['total_count']}")
        print(f"Percentage of overplayed sessions: {stats['percentage']}%")

    except Exception as e:
        print(f"[DEBUG] Error in main: {e}")
    finally:
        print("[DEBUG] Closing database connection...")
        db.close()
