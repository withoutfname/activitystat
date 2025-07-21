from PySide6.QtCore import QObject, Property, Slot, Signal, QCoreApplication, QStandardPaths
import os
import shutil
import sys
import json
import hashlib
import requests
import time
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
from PIL import Image as PILImage

class LibraryController(QObject):
    gamesListChanged = Signal()
    rawgMetadataFetched = Signal(int, str, str, int)

    def __init__(self, stats_service):
        super().__init__()
        self._stats_service = stats_service
        self._games_list = []
        self._base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        self._external_games_path = os.path.join(self._base_path, "external_games", "games.json")
        self._config = self._load_config()
        self._api_key = self._config.get("api_key", "")
        self._valid_genres = [
            "Action", "Adventure", "RPG", "Strategy", "Simulation", "Shooter", "Racing", "Sports",
            "Horror", "Sandbox", "Open World", "Survival", "Stealth", "Fighting", "Battle Royale",
            "Souls-like", "Roguelike", "Tactical", "Fantasy", "Cyberpunk", "Post-Apocalyptic",
            "Interactive Movie", "Narrative", "Single", "Multiplayer", "Co-op", "MMO"
        ]
        self._icons_dir = self._init_icons_directory()

    def _load_config(self):
            """Загружает конфигурацию из config.json в корне проекта."""
            config_path = os.path.join(self._base_path, "config.json")
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except FileNotFoundError:
                print(f"Ошибка: Файл конфигурации {config_path} не найден")
                return {}
            except json.JSONDecodeError as e:
                print(f"Ошибка декодирования JSON в файле конфигурации: {e}")
                return {}
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                return {}

    def _init_icons_directory(self):
        try:
            if os.name == 'nt':
                appdata_path = os.getenv('APPDATA')
            else:
                appdata_path = os.path.expanduser('~')
            icons_dir = os.path.join(appdata_path, "ActivityStats", "app_icons")
            os.makedirs(icons_dir, exist_ok=True)
            print(f"Icons directory initialized at: {icons_dir}")
            return icons_dir
        except Exception as e:
            print(f"Error initializing icons directory: {str(e)}")
            return ""

    @Property(list, notify=gamesListChanged)
    def gamesList(self):
        return self._games_list

    @Slot()
    def fetchGames(self):
        try:
            db_games = self._stats_service.get_games_list_with_rating()
            external_games = self.load_external_games()
            self._games_list = sorted(db_games + external_games, key=lambda x: x.get("total_hours", 0), reverse=True)
            self.gamesListChanged.emit()
        except Exception as e:
            print(f"Ошибка при загрузке игр: {e}")

    def load_external_games(self):
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
                            "icon_path": icon_path,
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
        print(f"Сохранение метаданных для app_id={app_id}, icon_path={icon_path}, genre={genre}, year={year}, rating={rating}")
        try:
            year = None if year == 0 else year
            self._stats_service.update_game_metadata(app_id, icon_path, genre, year, rating)
            self.fetchGames()
        except Exception as e:
            print(f"Ошибка сохранения метаданных: {e}")

    def get_icon_path_for_qml(self, absolute_path):
        if not absolute_path:
            return ""
        return f"file:///{absolute_path.replace(os.sep, '/')}"

    @Slot(str, result=str)
    def get_full_icon_path(self, icon_name):
        if not icon_name or not self._icons_dir:
            return ""
        return os.path.join(self._icons_dir, icon_name)

    @Slot(str, str, result=str)
    def copyIcon(self, source_path, app_id):
        try:
            if not os.path.exists(source_path):
                print(f"Ошибка: Исходный файл не существует: {source_path}")
                return ""
            if not self._icons_dir:
                print("Ошибка: Папка для иконок не инициализирована")
                return ""
            extension = os.path.splitext(source_path)[1]
            if not extension:
                print(f"Ошибка: У исходного файла нет расширения: {source_path}")
                return ""
            timestamp = int(time.time())
            new_file_name = f"{app_id}_icon_{timestamp}{extension}"
            destination_path = os.path.join(self._icons_dir, new_file_name)
            shutil.copy2(source_path, destination_path)
            print(f"Иконка скопирована из {source_path} в {destination_path}")
            return new_file_name
        except Exception as e:
            print(f"Ошибка копирования иконки: {str(e)}")
            return ""

    @Slot(str, result=str)
    def getIconUrl(self, icon_name):
        if not icon_name:
            return ""
        if icon_name.startswith(".."):
            full_path = os.path.abspath(os.path.join(self._base_path, icon_name))
        else:
            full_path = self.get_full_icon_path(icon_name)
        return self.get_icon_path_for_qml(full_path) if full_path else ""

    @Slot(int, str)
    def fetchRawgMetadata(self, app_id, game_name):
        print(f"Автопарсинг метаданных для app_id={app_id}, game_name={game_name}")
        temp_path = ""
        try:
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
            game_url = f"https://api.rawg.io/api/games/{game_id}?key={self._api_key}"
            game_response = requests.get(game_url)
            if game_response.status_code != 200:
                print(f"Ошибка получения данных игры из RAWG API: {game_response.status_code}")
                return
            game_data = game_response.json()
            year = 0
            if game_data.get("released"):
                try:
                    year = int(game_data["released"].split("-")[0])
                except (ValueError, IndexError):
                    print(f"Ошибка парсинга года выпуска для {game_name}")
            genres = [genre["name"] for genre in game_data.get("genres", [])]
            tags = [tag["name"] for tag in game_data.get("tags", [])]
            combined_genres_and_tags = genres + tags
            filtered_genres = [item for item in combined_genres_and_tags if item in self._valid_genres]
            filtered_genres = list(dict.fromkeys(filtered_genres))
            genres_string = ", ".join(filtered_genres) if filtered_genres else ""
            icon_path = ""
            image_url = game_data.get("background_image")
            if image_url:
                try:
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        extension = ".jpg"
                        timestamp = int(time.time())
                        temp_path = os.path.join(self._icons_dir, f"temp_{app_id}_icon_{timestamp}{extension}")
                        with open(temp_path, "wb") as image_file:
                            image_file.write(image_response.content)
                        icon_path = os.path.basename(temp_path)
                        print(f"Временная иконка для {game_name} сохранена: {temp_path}")
                    else:
                        print(f"Ошибка загрузки изображения: {image_response.status_code}")
                except Exception as e:
                    print(f"Ошибка сохранения изображения: {e}")
            self.rawgMetadataFetched.emit(app_id, icon_path or "", genres_string, year)
            print(f"Метаданные для {game_name} отправлены в QML")
        except Exception as e:
            print(f"Ошибка автопарсинга для {game_name}: {e}")

    @Slot(str, str, result=str)
    def saveIconToAppData(self, source_path, app_id):
        if not source_path:
            print("Source path is empty, returning empty string")
            return ""
        is_temp_icon = os.path.basename(source_path).startswith(f"temp_{app_id}_icon")
        import glob
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            pattern = os.path.join(self._icons_dir, f"{app_id}_icon{ext}")
            for old_icon_path in glob.glob(pattern):
                try:
                    os.remove(old_icon_path)
                    print(f"Deleted old icon: {old_icon_path}")
                except Exception as e:
                    print(f"Error deleting old icon {old_icon_path}: {str(e)}")
        if is_temp_icon:
            new_icon = self.copyIcon(source_path, app_id)
            if new_icon:
                try:
                    os.remove(source_path)
                    print(f"Deleted temp icon: {source_path}")
                except Exception as e:
                    print(f"Error deleting temp icon {source_path}: {str(e)}")
            return new_icon
        else:
            if source_path.startswith(self._icons_dir):
                print(f"Source path {source_path} is already in AppData, returning basename")
                return os.path.basename(source_path)
            else:
                return self.copyIcon(source_path, app_id)

    @Slot(str)
    def deleteTempIcon(self, temp_path):
        if not temp_path:
            return
        full_path = os.path.join(self._icons_dir, temp_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                print(f"Deleted temp icon: {full_path}")
            except Exception as e:
                print(f"Error deleting temp icon {full_path}: {str(e)}")

    @Slot(str, result=bool)
    def checkFileExists(self, file_path):
        return os.path.exists(file_path)

    @Slot(result=str)
    def exportToPdf(self):
        try:
            docs_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            if not docs_path:
                docs_path = os.path.expanduser("~")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = os.path.join(docs_path, f"GameLibrary_{timestamp}.pdf")
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            elements = []
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=18,
                alignment=1,
                spaceAfter=20
            )
            elements.append(Paragraph("My Game Library", title_style))
            for game in self._games_list:
                self._add_game_to_pdf(elements, game)
                elements.append(Spacer(1, 12))
            doc.build(elements)
            print(f"PDF generated at: {pdf_path}")
            return pdf_path
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return ""

    def _add_game_to_pdf(self, elements, game):
        styles = getSampleStyleSheet()
        name_style = ParagraphStyle(
            'GameName',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=6
        )
        elements.append(Paragraph(game.get('name', 'Unknown Game'), name_style))
        game_data = []
        img_path = self._get_image_path_for_pdf(game)
        img_element = None
        if img_path and os.path.exists(img_path):
            try:
                pil_img = PILImage.open(img_path)
                img_width, img_height = pil_img.size
                target_width = 2*inch
                target_height = 2*inch
                aspect = img_width / img_height
                if aspect > 1:
                    target_height = target_width / aspect
                else:
                    target_width = target_height * aspect
                img_element = Image(img_path, width=target_width, height=target_height)
            except Exception as e:
                print(f"Error processing image {img_path}: {str(e)}")
        metadata_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=10,
            leading=12
        )
        metadata = [
            Paragraph(f"<b>Hours Played:</b> {game.get('total_hours', 0):.1f}", metadata_style),
            Paragraph(f"<b>Sessions:</b> {game.get('session_count', 0)}", metadata_style),
            #Paragraph(f"<b>First Played:</b> {self._format_date(game.get('first_played'))}", metadata_style),
            #Paragraph(f"<b>Last Played:</b> {self._format_date(game.get('last_played'))}", metadata_style),
            #Paragraph(f"<b>Genre:</b> {game.get('genre', 'Unknown')}", metadata_style),
            Paragraph(f"<b>Year:</b> {game.get('year', 'N/A')}", metadata_style),
            Paragraph(f"<b>Rating:</b> {self._format_rating(game.get('rating'))}", metadata_style)
        ]
        metadata_table = Table([[m] for m in metadata], colWidths=[3.5*inch])
        metadata_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        row_data = [img_element or "", metadata_table]
        game_table = Table([row_data], colWidths=[2.5*inch, 3.5*inch])
        game_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(game_table)

    def _get_image_path_for_pdf(self, game):
        if not game.get('icon_path'):
            return None
        if game.get('is_external'):
            if game['icon_path'].startswith('../../external_games/'):
                return os.path.join(self._base_path, "external_games",
                                    game['icon_path'].replace('../../external_games/', ''))
            return game['icon_path'].replace('file:///', '')
        else:
            return self.get_full_icon_path(game['icon_path'])

    def _format_rating(self, rating):
        if rating == "like":
            return "👍 Liked"
        elif rating == "dislike":
            return "👎 Disliked"
        elif rating == "mixed":
            return "~ Mixed"
        return "Not rated"

    def _format_date(self, timestamp):
        if not timestamp or timestamp == "N/A":
            return "N/A"
        try:
            return time.strftime("%d-%m-%Y", time.gmtime(timestamp / 1000))
        except:
            return "N/A"
