from PySide6.QtCore import QObject, Property, Slot, Signal, QCoreApplication
import os
import shutil
import sys
import json
import hashlib

class LibraryController(QObject):
    gamesListChanged = Signal()

    def __init__(self, stats_service):
        super().__init__()
        self._stats_service = stats_service
        self._games_list = []
        self._base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        self._external_games_path = os.path.join(self._base_path, "external_games", "games.json")

    @Property(list, notify=gamesListChanged)
    def gamesList(self):
        return self._games_list

    @Slot()
    def fetchGames(self):
        """Обновляет список игр из сервиса и внешнего JSON с сортировкой по часам."""
        try:
            # Загружаем игры из БД
            db_games = self._stats_service.get_games_list_with_rating()

            # Загружаем внешние игры
            external_games = self.load_external_games()

            # Объединяем и сортируем по total_hours в убывающем порядке
            self._games_list = sorted(db_games + external_games, key=lambda x: x.get("total_hours", 0), reverse=True)
            self.gamesListChanged.emit()
        except Exception as e:
            print(f"Error fetching games: {e}")

    '''

    def load_external_games(self):
        """Читает данные из games.json и возвращает список игр."""
        external_games = []
        if os.path.exists(self._external_games_path):
            try:
                with open(self._external_games_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for game in data.get("games", []):
                        # Генерируем уникальный app_id на основе имени для копирования иконки
                        app_id = int(hashlib.md5(game.get("name", "").encode()).hexdigest(), 16) % (10**8)
                        icon_path = game.get("image", "")
                        if icon_path and not os.path.isabs(icon_path):  # Проверяем, что путь относительный
                            full_image_path = os.path.join(self._base_path, "external_games", icon_path)
                            if not os.path.exists(full_image_path):
                                print(f"Warning: Image not found at {full_image_path}")
                                icon_path = ""  # Если изображения нет, очищаем путь
                        external_game = {
                            "app_id": app_id,
                            "name": game.get("name", "Unknown Game"),
                            "icon_path": icon_path,  # Используем оригинальный относительный путь
                            "total_hours": game.get("total_hours", 0.0),
                            "first_played": game.get("first_played"),
                            "last_played": game.get("last_played"),
                            "session_count": game.get("session_count"),
                            "genre": game.get("genre"),
                            "year": game.get("year"),
                            "rating": game.get("rating"),
                            "is_external": True  # Устанавливаем флаг для сторонних игр
                        }
                        external_games.append(external_game)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"Error loading external games: {e}")
        return external_games

    '''


    def load_external_games(self):
        """Читает данные из games.json и возвращает список игр."""
        external_games = []
        if os.path.exists(self._external_games_path):
            try:
                with open(self._external_games_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for game in data.get("games", []):
                        # Генерируем уникальный app_id на основе имени
                        app_id = int(hashlib.md5(game.get("name", "").encode()).hexdigest(), 16) % (10**8)
                        icon_path = game.get("image", "")

                        # Формируем полный путь к изображению для внешних игр
                        if icon_path:
                            # Для внешних игр используем относительный путь от корня приложения
                            icon_path = f"../../external_games/{icon_path}"
                            # Проверяем существует ли файл
                            full_path = os.path.join(self._base_path, "external_games", game.get("image", ""))
                            if not os.path.exists(full_path):
                                print(f"Warning: External game image not found at {full_path}")
                                icon_path = ""  # Если файл не найден, оставляем пустым

                        external_game = {
                            "app_id": app_id,
                            "name": game.get("name", "Unknown Game"),
                            "icon_path": icon_path or "../../resources/app_icons/images.jpg",  # fallback
                            "total_hours": game.get("total_hours", 0.0),
                            "first_played": game.get("first_played"),
                            "last_played": game.get("last_played"),
                            "session_count": game.get("session_count"),
                            "genre": game.get("genre"),
                            "year": game.get("year"),
                            "rating": game.get("rating"),
                            "is_external": True
                        }
                        external_games.append(external_game)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"Error loading external games: {e}")
        return external_games

    @Slot(int, str)
    def fetchMetadata(self, app_id, game_name):
        print(f"Fetching metadata for app_id={app_id}, game_name={game_name}")

    @Slot(int, str, str, 'QVariant', str)
    def saveManualMetadata(self, app_id, icon_path, genre, year, rating=None):
        print(f"Saving manual metadata for app_id={app_id}, icon_path={icon_path}, genre={genre}, year={year}, rating={rating}")
        try:
            year = None if year == 0 else year
            self._stats_service.update_game_metadata(app_id, icon_path, genre, year, rating)
            self.fetchGames()
        except Exception as e:
            print(f"Error saving metadata: {e}")

    @Slot(str, str, result=str)
    def copyIcon(self, source_path, app_id):
        try:
            if not os.path.exists(source_path):
                print(f"Error: Source file does not exist: {source_path}")
                return ""
            extension = os.path.splitext(source_path)[1]
            if not extension:
                print(f"Error: Source file has no extension: {source_path}")
                return ""
            new_file_name = f"{app_id}_icon{extension}"
            destination_dir = os.path.join(self._base_path, "resources", "app_icons")
            os.makedirs(destination_dir, exist_ok=True)
            destination_path = os.path.join(destination_dir, new_file_name)
            shutil.copy2(source_path, destination_path)
            print(f"Copied icon from {source_path} to {destination_path}")
            return f"../../resources/app_icons/{new_file_name}"
        except Exception as e:
            print(f"Error copying icon: {str(e)}")
            return ""
