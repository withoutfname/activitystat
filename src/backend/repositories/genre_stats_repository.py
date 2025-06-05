import psycopg2
from psycopg2 import Error
from datetime import datetime

class Database:
    def __init__(self, dbname="activitydb", user="postgres", password="pass", host="localhost", port="5432"):
        self.connection = None
        self.cursor = None
        try:
            self.connection = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.connection.autocommit = True  # Включаем автокоммит
            self.cursor = self.connection.cursor()
            print("Database connection successful")
        except Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed")

class GenreStatsRepository:
    def __init__(self, db):
        self.db = db

    def get_main_genre(self, year):
        """Возвращает жанр с максимальным игровым временем за год"""
        query = '''
            SELECT g.genre, SUM(EXTRACT(EPOCH FROM (s.end_time - s.start_time))/3600) as total_hours
            FROM game_metadata g
            JOIN activity_sessions s ON g.app_id = s.app_id
            WHERE EXTRACT(YEAR FROM s.start_time) = %s
            AND g.genre IS NOT NULL
            GROUP BY g.genre
            ORDER BY total_hours DESC
            LIMIT 1;
        '''
        try:
            self.db.cursor.execute(query, (year,))
            result = self.db.cursor.fetchone()
            if result:
                genres, total_hours = result
                primary_genre = genres.split(',')[0].strip()  # Первый жанр
                return {'genre': primary_genre, 'hours': round(total_hours, 1)}
            return None
        except Exception as e:
            print(f"Error executing query: {e}")
            return None

    def get_genre_distribution(self, year):
        """Возвращает процентное распределение времени по жанрам"""
        query = '''
            SELECT g.genre, EXTRACT(EPOCH FROM (s.end_time - s.start_time))/3600 as hours
            FROM game_metadata g
            JOIN activity_sessions s ON g.app_id = s.app_id
            WHERE EXTRACT(YEAR FROM s.start_time) = %s
            AND g.genre IS NOT NULL
            AND s.end_time IS NOT NULL;
        '''
        try:
            self.db.cursor.execute(query, (year,))
            results = self.db.cursor.fetchall()
            if not results:
                return []

            # Агрегируем время по первому жанру
            genre_hours = {}
            for row in results:
                genres, hours = row
                if not genres:
                    continue
                primary_genre = genres.split(',')[0].strip()  # Первый жанр
                genre_hours[primary_genre] = genre_hours.get(primary_genre, 0) + hours

            total_hours = sum(genre_hours.values())
            if total_hours == 0:
                return []

            # Формируем распределение
            distribution = [
                {
                    'genre': genre,
                    'percentage': round((hours / total_hours) * 100, 1)
                }
                for genre, hours in genre_hours.items()
            ]
            # Сортируем по убыванию процента для удобства
            distribution.sort(key=lambda x: x['percentage'], reverse=True)
            return distribution
        except Exception as e:
            print(f"Error executing query: {e}")
            return []

    def get_single_vs_multiplayer(self, year):
        """Возвращает процент одиночных и мультиплеерных игр по времени"""
        query = '''
            SELECT g.genre, EXTRACT(EPOCH FROM (s.end_time - s.start_time))/3600 as hours
            FROM game_metadata g
            JOIN activity_sessions s ON g.app_id = s.app_id
            WHERE EXTRACT(YEAR FROM s.start_time) = %s
            AND g.genre IS NOT NULL
            AND s.end_time IS NOT NULL;
        '''
        try:
            self.db.cursor.execute(query, (year,))
            results = self.db.cursor.fetchall()
            single_hours = 0
            multi_hours = 0

            for row in results:
                genres, hours = row
                if not genres:  # Пропускаем, если жанры пустые
                    continue
                genres = [genre.strip().lower() for genre in genres.split(',')]
                has_single = 'single' in genres or 'singleplayer' in genres
                has_multi = 'multiplayer' in genres

                if has_multi:
                    # Если есть Multiplayer, всё время идет в multi_hours
                    multi_hours += hours
                elif has_single:
                    # Если есть только Single/Singleplayer, время идет в single_hours
                    single_hours += hours
                # Если нет ни одного из тегов, время не учитывается

            total_hours = single_hours + multi_hours
            if total_hours == 0:
                return {'singleplayer': 0, 'multiplayer': 0}

            return {
                'singleplayer': round((single_hours / total_hours) * 100, 1),
                'multiplayer': round((multi_hours / total_hours) * 100, 1)
            }
        except Exception as e:
            print(f"Error executing query: {e}")
            return {'singleplayer': 0, 'multiplayer': 0}

if __name__ == "__main__":
    # Подключение к базе данных
    try:
        db = Database(dbname="activitydb", user="postgres", password="pass", host="localhost", port="5432")

        # Инициализация репозитория
        repo = GenreStatsRepository(db)

        # Получение результатов для 2025 года
        print("\nРезультаты для 2025 года:")

        # Основной жанр
        main_genre = repo.get_main_genre(2025)
        print(f"Основной жанр: {main_genre['genre']}: {main_genre['hours']} hours" if main_genre else "Основной жанр: N/A")

        # Распределение по жанрам
        genre_distribution = repo.get_genre_distribution(2025)
        print("Распределение по жанрам:",
              ', '.join([f"{g['genre']}: {g['percentage']}%" for g in genre_distribution]) if genre_distribution else "N/A")

        # Одиночные vs мультиплеерные
        single_vs_multi = repo.get_single_vs_multiplayer(2025)
        print(f"Singleplayer: {single_vs_multi['singleplayer']}%, Multiplayer: {single_vs_multi['multiplayer']}%")

    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        db.close()
