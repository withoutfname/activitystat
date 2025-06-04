from PySide6.QtCore import QObject, Property, Slot, Signal

class DashboardController(QObject):
    intervalChanged = Signal()
    availableYearsChanged = Signal()
    currentYearChanged = Signal(int)
    yearStatsChanged = Signal(dict)  # Новый сигнал для статистики года

    def __init__(self, dashboard_service):
        super().__init__()
        self.dashboard_service = dashboard_service
        self._availableYears = []
        self._currentYear = 0
        self._yearStats = {}  # Новое свойство для хранения статистики
        self.refreshYears()

    @Property(int, notify=currentYearChanged)
    def currentYear(self):
        return self._currentYear

    @currentYear.setter
    def currentYear(self, year):
        year = int(year)
        if self._currentYear != year:
            print(f"[Python] Setting new year: {year}")
            self._currentYear = year
            self.currentYearChanged.emit(year)
            self.updateYearStats()  # Обновляем статистику при изменении года
            self.intervalChanged.emit()

    @Property('QVariantList', notify=availableYearsChanged)
    def availableYears(self):
        return self._availableYears

    @Property('QVariantMap', notify=yearStatsChanged)
    def yearStats(self):
        return self._yearStats

    @Slot()
    def refreshYears(self):
        print("[Python] Refreshing available years")
        new_years = self.dashboard_service.get_unique_years() or []
        new_years = sorted(new_years, reverse=True)

        if new_years != self._availableYears:
            self._availableYears = new_years
            self.availableYearsChanged.emit()

            if self._currentYear not in self._availableYears and self._availableYears:
                self.currentYear = self._availableYears[0]

    @Slot()
    def updateYearStats(self):
        """Обновляет статистику для текущего года"""
        if self._currentYear:
            stats = self.dashboard_service.get_year_stats(self._currentYear)
            if stats:
                self._yearStats = stats
                self.yearStatsChanged.emit(self._yearStats)
