from PySide6.QtCore import QObject, Property, Slot, Signal, QDate
from datetime import datetime, timedelta

class DashboardController(QObject):
    intervalChanged = Signal()

    def __init__(self, stats_service):
        super().__init__()
        self.stats_service = stats_service
        self._currentDate = datetime.today()
        self._currentYear = self._currentDate.year
        self._trackingStartDate = self.stats_service.get_tracking_start_date()
        print("DashboardController initialized")

    @Property(int, notify=intervalChanged)
    def currentYear(self):
        return self._currentYear
