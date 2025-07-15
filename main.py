import sys
import os
import io


from PySide6.QtCore import QUrl, QtMsgType, qInstallMessageHandler
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
from src.backend.database import Database
from src.backend.services import StatsService, DashboardService
from src.frontend.controllers import DashboardController, TimeController, LibraryController
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

    # Initialize repositories and service
    stats_service = StatsService(db)
    dashboard_service = DashboardService(db)

    # Create controllers
    try:
        dashboard_controller = DashboardController(dashboard_service)
        time_controller = TimeController(stats_service)
        library_controller = LibraryController(stats_service)
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
