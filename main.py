import sys
import os
import io
import json

from PySide6.QtCore import QUrl, QtMsgType, qInstallMessageHandler
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
from src.backend.database.database import Database
from src.backend.services import StatsService, DashboardService, BackupService
from src.controllers import DashboardController, TimeController, LibraryController, BackupController, AiController
from PySide6.QtQuickControls2 import QQuickStyle

def qt_message_handler(mode, context, message):
    try:
        if mode == QtMsgType.QtInfoMsg:
            level = 'INFO'
        elif mode == QtMsgType.QtWarningMsg:
            level = 'WARNING'
        elif mode == QtMsgType.QtCriticalMsg:
            level = 'CRITICAL'
        elif mode == QtMsgType.QtFatalMsg:
            level = 'FATAL'
        else:
            level = 'DEBUG'

        # Принудительно кодируем вывод в UTF-8
        sys.stdout.buffer.write(f"[QML {level}] {message}\n".encode('utf-8', errors='replace'))
        sys.stdout.flush()
    except Exception as e:
        print(f"Error in message handler: {e}")

    # Выводим только QML сообщения (console.log попадает в QtInfoMsg)
    if 'qml' in context.file.lower() or context.file.endswith('.qml'):
        print(f"[QML {level}] {message}")


def load_config():
    """Загружает конфигурацию из config.json в корне проекта."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config.json")
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

if __name__ == "__main__":
    print("Starting application...")

    # Устанавливаем обработчик сообщений ДО создания QApplication
    qInstallMessageHandler(qt_message_handler)

    QQuickStyle.setStyle("Fusion")  # Или "Fusion", "Basic"
    app = QApplication(sys.argv)
    print("QApplication created")

    # Initialize database
    try:
        db = Database()
        print("Database initialized")
    except Exception as e:
        print(f"Database error: {e}")
        sys.exit(-1)

    config = load_config()
    db_config = config.get("database", {})

    # Initialize repositories and service
    stats_service = StatsService(db)
    dashboard_service = DashboardService(db)
    backup_service = BackupService({
        'dbname': db_config.get("database"),
        'user': db_config.get("user"),
        'password': db_config.get("password"),
        'host': db_config.get("host"),
        'port': str(db_config.get("port"))
    }, db)

    # Create controllers
    try:
        dashboard_controller = DashboardController(dashboard_service)
        time_controller = TimeController(stats_service)
        library_controller = LibraryController(stats_service)
        backup_controller = BackupController(backup_service)
        ai_controller = AiController(stats_service)
        print("Controllers created")
    except Exception as e:
        print(f"Controller error: {e}")
        sys.exit(-1)

    # Set up QML engine
    print("Setting up QML engine...")
    engine = QQmlApplicationEngine()

    # Set controllers in QML context
    engine.rootContext().setContextProperty("dashboardController", dashboard_controller)
    engine.rootContext().setContextProperty("timeController", time_controller)
    engine.rootContext().setContextProperty("libraryController", library_controller)
    engine.rootContext().setContextProperty("backupController", backup_controller)
    engine.rootContext().setContextProperty("aiController", ai_controller)
    print("Controllers set in QML context")

    # Load QML with absolute path
    print("Loading QML...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    qml_path = os.path.join(current_dir, "ui/main.qml")

    if not os.path.exists(qml_path):
        print(f"Error: QML file {qml_path} not found")
        sys.exit(-1)

    engine.load(QUrl.fromLocalFile(qml_path))
    print(f"QML file loaded: {qml_path}")

    if not engine.rootObjects():
        print("Error: No root objects loaded")
        sys.exit(-1)

    print("QML loaded successfully")
    sys.exit(app.exec())
