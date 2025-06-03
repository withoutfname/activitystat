from src.backend.database import Database

class AppRepository:
    def __init__(self, db):
        self.db = db

    def get_top_games(self, start_days=None, end_days=None, limit=None):
        query = """
            SELECT COALESCE(a.alias, a.name) as name,
                   SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600.0 as hours
            FROM activity_sessions s
            JOIN apps a ON s.app_id = a.id
            WHERE s.end_time IS NOT NULL
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

        query += " GROUP BY a.id, a.alias, a.name ORDER BY hours DESC"
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)
        self.db.cursor.execute(query, params)
        result = self.db.cursor.fetchall()
        result = [(row[0], float(row[1])) for row in result] if result else []
        return result

    def get_games_list(self):
        """Возвращает список всех игр с названием, датами первого и последнего запуска, общим временем, количеством сессий, жанром, годом и путём к иконке."""
        query = """
            SELECT 
                COALESCE(a.alias, a.name) as name,
                MIN(s.start_time) as first_played,
                MAX(s.end_time) as last_played,
                SUM(EXTRACT(EPOCH FROM (end_time - start_time))) / 3600.0 as total_hours,
                COUNT(s.id) as session_count,
                gm.genre,
                gm.year,
                gm.icon_path,
                a.id as app_id  -- Добавляем app_id
            FROM activity_sessions s
            JOIN apps a ON s.app_id = a.id
            LEFT JOIN game_metadata gm ON a.id = gm.app_id
            WHERE s.end_time IS NOT NULL
            GROUP BY a.id, a.alias, a.name, gm.genre, gm.year, gm.icon_path
            ORDER BY total_hours DESC
        """
        self.db.cursor.execute(query)
        result = self.db.cursor.fetchall()
        # Преобразуем результат в список словарей для удобства
        games_list = [
            {
                "name": row[0],
                "first_played": row[1].isoformat() if row[1] else None,
                "last_played": row[2].isoformat() if row[2] else None,
                "total_hours": float(row[3]) if row[3] else 0.0,
                "session_count": int(row[4]) if row[4] else 0,
                "genre": row[5] if row[5] is not None else "Unknown",
                "year": int(row[6]) if row[6] is not None else None,
                "icon_path": row[7] if row[7] is not None else "../../resources/app_icons/images.jpg",
                "app_id": row[8]  # Добавляем app_id в словарь
            }
            for row in result
        ] if result else []
        return games_list

    def update_game_metadata(self, app_id, icon_path, genre, year):
        """Обновляет или добавляет метаданные для игры в таблице game_metadata."""
        # Очищаем жанры перед сохранением
        if genre:
            genre = genre.strip()
            if not genre:
                genre = None
        print(f"Updating metadata for app_id={app_id}: icon_path={icon_path}, genre={genre}, year={year}")
        query = """
            INSERT INTO game_metadata (app_id, icon_path, genre, year)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (app_id)
            DO UPDATE SET
                icon_path = EXCLUDED.icon_path,
                genre = EXCLUDED.genre,
                year = EXCLUDED.year
        """
        self.db.cursor.execute(query, (app_id, icon_path, genre, year))
        self.db.connection.commit()