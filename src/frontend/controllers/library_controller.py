from PySide6.QtCore import QObject, Property, Slot, Signal, QCoreApplication
import os
import shutil
import sys
import json
import hashlib
import requests

class LibraryController(QObject):
    gamesListChanged = Signal()
    rawgMetadataFetched = Signal(int, str, str, int)  # Сигнал для передачи спарсенных данных: app_id, icon_path, genres, year

    def __init__(self, stats_service):
        super().__init__()
        self._stats_service = stats_service
        self._games_list = []
        self._base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        self._external_games_path = os.path.join(self._base_path, "external_games", "games.json")
        self._api_key = "0a6d31758d334f5fbba869e536259048"  # Ключ API RAWG
        # Список допустимых жанров из QML
        self._valid_genres = [
            "Action", "Adventure", "RPG", "Strategy", "Simulation", "Shooter", "Racing", "Sports",
            "Horror", "Sandbox", "Open World", "Survival", "Stealth", "Fighting", "Battle Royale",
            "Souls-like", "Roguelike", "Tactical", "Fantasy", "Cyberpunk", "Post-Apocalyptic",
            "Interactive Movie", "Narrative", "Single", "Multiplayer", "Co-op", "MMO"
        ]

    @Property(list, notify=gamesListChanged)
    def gamesList(self):
        return self._games_list

    @Slot()
    def fetchGames(self):
        """Обновляет список игр из сервиса и внешнего JSON с сортировкой по часам."""
        try:
            db_games = self._stats_service.get_games_list_with_rating()
            external_games = self.load_external_games()
            self._games_list = sorted(db_games + external_games, key=lambda x: x.get("total_hours", 0), reverse=True)
            self.gamesListChanged.emit()
        except Exception as e:
            print(f"Ошибка при загрузке игр: {e}")

    def load_external_games(self):
        """Читает данные из games.json и возвращает список игр."""
        external_games = []
        if os.path.exists(self._external_games_path):
            try:
                with open(self._external_games_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for game in data.get("games", []):
                        app_id = int(hashlib.md5(game.get("name", "").encode()).hexdigest(), 16) % (10**8)
                        icon_path = game.get("image", "")
                        if icon_path:
                            icon_path = f"../../external_games/{icon_path}"
                            full_path = os.path.join(self._base_path, "external_games", game.get("image", ""))
                            if not os.path.exists(full_path):
                                print(f"Предупреждение: Изображение внешней игры не найдено по пути {full_path}")
                                icon_path = ""
                        external_game = {
                            "app_id": app_id,
                            "name": game.get("name", "Unknown Game"),
                            "icon_path": icon_path or "../../resources/app_icons/images.jpg",
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
                print(f"Ошибка декодирования JSON: {e}")
            except Exception as e:
                print(f"Ошибка загрузки внешних игр: {e}")
        return external_games

    @Slot(int, str)
    def fetchMetadata(self, app_id, game_name):
        print(f"Запрос метаданных для app_id={app_id}, game_name={game_name}")

    @Slot(int, str, str, 'QVariant', str)
    def saveManualMetadata(self, app_id, icon_path, genre, year, rating=None):
        """Сохраняет метаданные игры."""
        print(f"Сохранение метаданных для app_id={app_id}, icon_path={icon_path}, genre={genre}, year={year}, rating={rating}")
        try:
            year = None if year == 0 else year
            self._stats_service.update_game_metadata(app_id, icon_path, genre, year, rating)
            self.fetchGames()
        except Exception as e:
            print(f"Ошибка сохранения метаданных: {e}")

    @Slot(str, str, result=str)
    def copyIcon(self, source_path, app_id):
        """Копирует иконку в resources/app_icons и возвращает относительный путь."""
        try:
            if not os.path.exists(source_path):
                print(f"Ошибка: Исходный файл не существует: {source_path}")
                return ""
            extension = os.path.splitext(source_path)[1]
            if not extension:
                print(f"Ошибка: У исходного файла нет расширения: {source_path}")
                return ""
            new_file_name = f"{app_id}_icon{extension}"
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
                destination_dir = os.path.join(base_path, "resources", "app_icons")
            else:
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
                destination_dir = os.path.join(base_path, "resources", "app_icons")
            os.makedirs(destination_dir, exist_ok=True)
            destination_path = os.path.join(destination_dir, new_file_name)
            shutil.copy2(source_path, destination_path)
            print(f"Иконка скопирована из {source_path} в {destination_path}")
            if getattr(sys, 'frozen', False):
                return f"resources/app_icons/{new_file_name}"
            else:
                return f"../../resources/app_icons/{new_file_name}"
        except Exception as e:
            print(f"Ошибка копирования иконки: {str(e)}")
            return ""

    @Slot(int, str)
    def fetchRawgMetadata(self, app_id, game_name):
        """Получает метаданные игры из RAWG API и отправляет их в QML."""
        print(f"Автопарсинг метаданных для app_id={app_id}, game_name={game_name}")
        try:
            # Шаг 1: Поиск игры по имени
            search_url = f"https://api.rawg.io/api/games?key={self._api_key}&search={game_name}&page_size=1"
            search_response = requests.get(search_url)
            if search_response.status_code != 200:
                print(f"Ошибка поиска игры в RAWG API: {search_response.status_code}")
                return

            search_data = search_response.json()
            if not search_data.get("results"):
                print(f"Игра '{game_name}' не найдена в RAWG API")
                return

            game_id = search_data["results"][0]["id"]

            # Шаг 2: Получение полных данных игры
            game_url = f"https://api.rawg.io/api/games/{game_id}?key={self._api_key}"
            game_response = requests.get(game_url)
            if game_response.status_code != 200:
                print(f"Ошибка получения данных игры из RAWG API: {game_response.status_code}")
                return

            game_data = game_response.json()

            # Извлечение года
            year = 0
            if game_data.get("released"):
                try:
                    year = int(game_data["released"].split("-")[0])
                except (ValueError, IndexError):
                    print(f"Ошибка парсинга года выпуска для {game_name}")

            # Извлечение и фильтрация жанров и тегов
            genres = [genre["name"] for genre in game_data.get("genres", [])]
            tags = [tag["name"] for tag in game_data.get("tags", [])]
            combined_genres_and_tags = genres + tags
            filtered_genres = [item for item in combined_genres_and_tags if item in self._valid_genres]
            # Удаляем дубликаты, сохраняя порядок
            filtered_genres = list(dict.fromkeys(filtered_genres))
            genres_string = ", ".join(filtered_genres) if filtered_genres else ""

            # Загрузка и сохранение изображения
            icon_path = ""
            temp_path = ""
            image_url = game_data.get("background_image")
            if image_url:
                try:
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        # Определяем расширение файла из URL или по умолчанию .jpg
                        extension = os.path.splitext(image_url)[1].lower()
                        if not extension or extension not in [".jpg"]:
                            extension = ".jpg"
                        # Временный файл для сохранения изображения
                        temp_path = os.path.join(self._base_path, f"temp_{app_id}_icon{extension}")
                        temp_dir = os.path.dirname(temp_path)
                        os.makedirs(temp_dir, exist_ok=True)
                        with open(temp_path, "wb") as image_file:
                            image_file.write(image_response.content)
                        # Копируем изображение с помощью copyIcon
                        icon_path = self.copyIcon(temp_path, str(app_id))
                        print(f"Изображение для {game_name} успешно сохранено: {icon_path}")
                    else:
                        print(f"Ошибка загрузки изображения: {image_response.status_code}")
                except Exception as e:
                    print(f"Ошибка сохранения изображения: {e}")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

            # Отправляем данные в QML через сигнал
            self.rawgMetadataFetched.emit(app_id, icon_path or "", genres_string, year)
            print(f"Метаданные для {game_name} отправлены в QML")
        except Exception as e:
            print(f"Ошибка автопарсинга для {game_name}: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
