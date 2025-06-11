from PySide6.QtCore import QObject, Property, Slot, Signal, QCoreApplication
import os
import shutil
import sys

class LibraryController(QObject):
    gamesListChanged = Signal()  # Заменяем pyqtSignal на Signal

    def __init__(self, stats_service):
        super().__init__()
        self._stats_service = stats_service
        self._games_list = []
        # Базовый путь к проекту для папки resources/app_icons
        self._base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

    @Property(list, notify=gamesListChanged)  # Заменяем pyqtProperty на Property
    def gamesList(self):
        return self._games_list

    @Slot()  # Заменяем pyqtSlot на Slot
    def fetchGames(self):
        """Обновляет список игр из сервиса."""
        try:
            self._games_list = self._stats_service.get_games_list_with_rating()
            self.gamesListChanged.emit()
        except Exception as e:
            print(f"Error fetching games: {e}")

    @Slot(int, str)
    def fetchMetadata(self, app_id, game_name):
        """Запускает парсер для получения метаданных."""
        print(f"Fetching metadata for app_id={app_id}, game_name={game_name}")

    @Slot(int, str, str, 'QVariant', str)
    def saveManualMetadata(self, app_id, icon_path, genre, year, rating=None):
        """Сохраняет метаданные вручную, включая рейтинг."""
        print(f"Saving manual metadata for app_id={app_id}, icon_path={icon_path}, genre={genre}, year={year}, rating={rating}")
        try:
            year = None if year == 0 else year
            self._stats_service.update_game_metadata(app_id, icon_path, genre, year, rating)
            self.fetchGames()
        except Exception as e:
            print(f"Error saving metadata: {e}")

    @Slot(str, str, result=str)
    def copyIcon(self, source_path, app_id):
        """Копирует иконку в папку resources/app_icons с новым именем."""
        try:
            # Проверяем, существует ли исходный файл
            if not os.path.exists(source_path):
                print(f"Error: Source file does not exist: {source_path}")
                return ""

            # Извлекаем расширение файла
            extension = os.path.splitext(source_path)[1]
            if not extension:
                print(f"Error: Source file has no extension: {source_path}")
                return ""

            # Формируем новое имя файла
            new_file_name = f"{app_id}_icon{extension}"
            # Формируем полный путь к папке назначения
            destination_dir = os.path.join(self._base_path, "resources", "app_icons")
            print(f"Destination directory: {destination_dir}")  # Для отладки
            os.makedirs(destination_dir, exist_ok=True)  # Создаём папку, если её нет
            destination_path = os.path.join(destination_dir, new_file_name)

            # Копируем файл
            shutil.copy2(source_path, destination_path)
            print(f"Copied icon from {source_path} to {destination_path}")

            # Возвращаем относительный путь для QML
            return f"../../resources/app_icons/{new_file_name}"
        except Exception as e:
            print(f"Error copying icon: {str(e)}")
            return ""
