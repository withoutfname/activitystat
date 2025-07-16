# src/controllers/backup_controller/backup_controller.py
from PySide6.QtCore import QObject, Slot, Signal

class BackupController(QObject):
    def __init__(self, backup_service):
        super().__init__()
        self.backup_service = backup_service
        self.backup_service.backupCompleted.connect(self._on_backup_completed)
        self.backup_service.restoreCompleted.connect(self._on_restore_completed)

    backupStatus = Signal(bool, str)
    restoreStatus = Signal(bool, str)

    @Slot(str)
    def backupDatabase(self, file_path):
        self.backup_service.backup_database(file_path)

    @Slot(str)
    def restoreDatabase(self, file_path):
        self.backup_service.restore_database(file_path)

    def _on_backup_completed(self, success, message):
        self.backupStatus.emit(success, message)

    def _on_restore_completed(self, success, message):
        self.restoreStatus.emit(success, message)
