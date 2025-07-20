import sys
import os

# Добавляем корень проекта в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from src.backend.database.database import Database

class StreakStatsRepository:
    def __init__(self, db):
        self.db = db

    def get_longest_gaming_streak_in_year(self, year):
        """Возвращает самый длинный стрик игровых дней в указанном году"""
        query = """
        WITH RECURSIVE dates AS (
            SELECT CAST(MIN(CAST(start_time AS date)) AS date) AS date
            FROM activity_sessions
            WHERE EXTRACT(YEAR FROM start_time) = %s AND end_time IS NOT NULL
            UNION ALL
            SELECT CAST(date + INTERVAL '1 day' AS date)
            FROM dates
            WHERE date < (
                SELECT CAST(MAX(CAST(start_time AS date)) AS date)
                FROM activity_sessions
                WHERE EXTRACT(YEAR FROM start_time) = %s AND end_time IS NOT NULL
            )
        ),
        gaming_days AS (
            SELECT CAST(start_time AS date) AS game_date
            FROM activity_sessions
            WHERE EXTRACT(YEAR FROM start_time) = %s AND end_time IS NOT NULL
            GROUP BY CAST(start_time AS date)
        ),
        streaks AS (
            SELECT
                d.date,
                CASE
                    WHEN gd.game_date IS NOT NULL THEN 0
                    ELSE 1
                END AS is_break,
                SUM(CASE WHEN gd.game_date IS NOT NULL THEN 0 ELSE 1 END) OVER (
                    ORDER BY d.date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS group_id
            FROM dates d
            LEFT JOIN gaming_days gd ON d.date = gd.game_date
        ),
        streak_lengths AS (
            SELECT
                group_id,
                COUNT(*) AS streak_length,
                MIN(date) AS start_date,
                MAX(date) AS end_date
            FROM streaks
            WHERE is_break = 0
            GROUP BY group_id
            HAVING COUNT(*) > 1
            ORDER BY streak_length DESC
            LIMIT 1
        )
        SELECT
            streak_length,
            start_date,
            end_date
        FROM streak_lengths;
        """
        self.db.cursor.execute(query, (year, year, year))
        result = self.db.cursor.fetchone()
        return {
            "length": result[0] if result else 0,
            "start_date": result[1].strftime('%d.%m') if result and result[1] else None,
            "end_date": result[2].strftime('%d.%m') if result and result[2] else None
        } if result else {"length": 0, "start_date": None, "end_date": None}

    def get_longest_game_streak_in_year(self, year):
        """Возвращает самый длинный стрик для конкретной игры в указанном году"""
        query = """
        WITH game_dates AS (
            SELECT
                a.alias,
                CAST(s.start_time AS date) AS game_date,
                ROW_NUMBER() OVER (PARTITION BY a.alias ORDER BY CAST(s.start_time AS date)) AS rn,
                CAST(s.start_time AS date) - ROW_NUMBER() OVER (PARTITION BY a.alias ORDER BY CAST(s.start_time AS date)) * INTERVAL '1 day' AS group_id
            FROM activity_sessions s
            JOIN apps a ON s.app_id = a.id
            WHERE EXTRACT(YEAR FROM s.start_time) = %s AND s.end_time IS NOT NULL
        ),
        game_streaks AS (
            SELECT
                alias,
                COUNT(*) AS streak_length,
                MIN(game_date) AS start_date,
                MAX(game_date) AS end_date
            FROM game_dates
            GROUP BY alias, group_id
            HAVING COUNT(*) > 1
        ),
        max_streak_per_game AS (
            SELECT
                alias,
                MAX(streak_length) AS max_length,
                MAX(end_date) AS latest_end_date
            FROM game_streaks
            GROUP BY alias
        )
        SELECT
            gs.alias,
            gs.streak_length AS max_length,
            gs.start_date,
            gs.end_date
        FROM game_streaks gs
        JOIN max_streak_per_game msg ON gs.alias = msg.alias AND gs.streak_length = msg.max_length AND gs.end_date = msg.latest_end_date
        ORDER BY max_length DESC
        LIMIT 1;
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        return {
            "game": result[0] if result else None,
            "length": result[1] if result else 0,
            "start_date": result[2].strftime('%d.%m') if result and result[2] else None,
            "end_date": result[3].strftime('%d.%m') if result and result[3] else None
        } if result else {"game": None, "length": 0, "start_date": None, "end_date": None}

    def get_longest_break_in_year(self, year):
        """Returns the longest break between gaming sessions in the specified year"""
        query = """
        WITH gaming_days AS (
            SELECT DISTINCT CAST(start_time AS date) AS game_date
            FROM activity_sessions
            WHERE EXTRACT(YEAR FROM start_time) = %s
              AND end_time IS NOT NULL
        ),
        date_ranges AS (
            SELECT
                game_date,
                LEAD(game_date) OVER (ORDER BY game_date) AS next_game_date
            FROM gaming_days
        ),
        breaks AS (
            SELECT
                game_date AS break_start,
                next_game_date AS break_end,
                next_game_date - game_date - 1 AS break_days
            FROM date_ranges
            WHERE next_game_date IS NOT NULL
              AND next_game_date > game_date + 1
        )
        SELECT
            break_days,
            break_start,
            break_end - 1 AS end_date
        FROM breaks
        ORDER BY break_days DESC
        LIMIT 1;
        """
        self.db.cursor.execute(query, (year,))
        result = self.db.cursor.fetchone()
        return {
            "length": result[0] if result else 0,
            "start_date": result[1].strftime('%d.%m') if result and result[1] else None,
            "end_date": result[2].strftime('%d.%m') if result and result[2] else None
        } if result else {"length": 0, "start_date": None, "end_date": None}

if __name__ == "__main__":
    try:
        # Подключение к базе данных
        print("[DEBUG] Initializing database connection...")
        db = Database(dbname="activitydb", user="postgres", password="pass", host="localhost", port="5432")
        print("[DEBUG] Database connection established")
        repo = StreakStatsRepository(db)

        # Тестируем для 2025 года
        year = 2025
        print(f"\nTesting StreakStatsRepository for year {year}:\n")

        # Тест get_longest_gaming_streak_in_year
        print("Testing get_longest_gaming_streak_in_year...")
        gaming_streak = repo.get_longest_gaming_streak_in_year(year)
        print(f"Longest gaming streak: {gaming_streak['length']} days, from {gaming_streak['start_date']} to {gaming_streak['end_date']}")

        # Тест get_longest_game_streak_in_year
        print("\nTesting get_longest_game_streak_in_year...")
        game_streak = repo.get_longest_game_streak_in_year(year)
        print(f"Longest game streak: {game_streak['game']} - {game_streak['length']} days, from {game_streak['start_date']} to {game_streak['end_date']}")

        # Тест get_longest_break_in_year
        print("\nTesting get_longest_break_in_year...")
        break_streak = repo.get_longest_break_in_year(year)
        print(f"Longest break: {break_streak['length']} days, from {break_streak['start_date']} to {break_streak['end_date']}")

    except Exception as e:
        print(f"[DEBUG] Error in main: {e}")
    finally:
        print("[DEBUG] Closing database connection...")
        db.close()
