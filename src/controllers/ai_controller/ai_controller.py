# src/controllers/ai_controller/ai_controller.py
from PySide6.QtCore import QObject

class AiController(QObject):
    def __init__(self, stats_service):
        super().__init__()

