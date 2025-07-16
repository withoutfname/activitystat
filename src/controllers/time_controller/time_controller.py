from PySide6.QtCore import QObject, Property, Slot, Signal
from datetime import datetime, timedelta

class TimeController(QObject):
    intervalChanged = Signal()

    def __init__(self, stats_service):
        super().__init__()
        self.stats_service = stats_service
        self._startDays = 0
        self._endDays = 0
        self._currentDate = datetime.today()
        print("TimeController initialized")

    @Property(int, notify=intervalChanged)
    def startDays(self):
        return self._startDays

    @Property(int, notify=intervalChanged)
    def endDays(self):
        return self._endDays

    @Property(float, notify=intervalChanged)
    def avgSessionTime(self):
        try:
            result = self.stats_service.get_avg_interval_playtime(self._startDays, self._endDays)
            return float(result) if result is not None else 0.0
        except Exception as e:
            print(f"Error in avgSessionTime: {e}")
            return 0.0

    @Property(str, notify=intervalChanged)
    def startDate(self):
        date = self._currentDate - timedelta(days=self._startDays)
        return date.strftime("%Y-%m-%d")

    @Property(str, notify=intervalChanged)
    def endDate(self):
        date = self._currentDate - timedelta(days=self._endDays)
        return date.strftime("%Y-%m-%d")

    @Property(int, constant=True)
    def maxIntervalDays(self):
        try:
            result = self.stats_service.get_max_interval_days()
            return result
        except Exception as e:
            print(f"Error in maxIntervalDays: {e}")
            return 30

    @Slot(int, int)
    def setIntervalRange(self, startDays, endDays):
        if self._startDays != startDays or self._endDays != endDays:
            self._startDays = startDays
            self._endDays = endDays
            self.intervalChanged.emit()
            #print(f"Interval updated: startDays={startDays}, endDays={endDays}")

    @Property(float, notify=intervalChanged)
    def avgDayPlaytime(self):
        try:
            result = self.stats_service.get_avg_day_playtime(self._startDays, self._endDays)
            return float(result) if result is not None else 0.0
        except Exception as e:
            print(f"Error in avgDayPlaytime: {e}")
            return 0.0

    @Property(int, notify=intervalChanged)
    def simpSessionCount(self):
        try:
            result = self.stats_service.get_simp_session_count(self._startDays, self._endDays)
            return int(result) if result is not None else 0
        except Exception as e:
            print(f"Error in simpSessionCount: {e}")
            return 0

    @Property(int, notify=intervalChanged)
    def fullSessionCount(self):
        try:
            result = self.stats_service.get_full_session_count(self._startDays, self._endDays)
            return int(result) if result is not None else 0
        except Exception as e:
            print(f"Error in fullSessionCount: {e}")
            return 0

    @Property(float, notify=intervalChanged)  # Изменил на float, чтобы соответствовать QML
    def totalFullPlaytime(self):
        try:
            result = self.stats_service.get_full_total_playtime(self._startDays, self._endDays)
            return float(result) if result is not None else 0.0
        except Exception as e:
            print(f"Error in totalFullPlaytime: {e}")
            return 0.0

    @Property('QVariantList', notify=intervalChanged)
    def maxSessionDuration(self):
        try:
            duration, game_name, date = self.stats_service.get_max_session_duration(self._startDays, self._endDays)
            return [float(duration), game_name if game_name else '', date if date else '']
        except Exception as e:
            print(f"Error in maxSessionDuration: {e}")
            return [0.0, '', '']

    @Property('QVariantList', notify=intervalChanged)
    def maxDailyGameSession(self):
        try:
            duration, date, game_name, session_count = self.stats_service.get_max_daily_game_session(self._startDays, self._endDays)
            return [float(duration), date if date else '', game_name if game_name else '', int(session_count)]
        except Exception as e:
            print(f"Error in maxDailyGameSession: {e}")
            return [0.0, '', '', 0]

    @Property('QVariantList', notify=intervalChanged)
    def maxDailyTotalDuration(self):
        try:
            duration, date, game_details = self.stats_service.get_max_daily_total_duration(self._startDays, self._endDays)
            return [float(duration), date if date else '', game_details if game_details else '']
        except Exception as e:
            print(f"Error in maxDailyTotalDuration: {e}")
            return [0.0, '', '']

    @Property('QVariantList', notify=intervalChanged)
    def playtimeByDayOfWeek(self):
        try:
            playtime = self.stats_service.get_playtime_by_day_of_week(self._startDays, self._endDays)
            return [float(x) for x in playtime]
        except Exception as e:
            print(f"Error in playtimeByDayOfWeek: {e}")
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    @Property('QVariantList', notify=intervalChanged)
    def playtimeByTimeOfDay(self):
        try:
            playtime = self.stats_service.get_playtime_by_time_of_day(self._startDays, self._endDays)
            return [float(playtime.get("Morning", 0.0)), float(playtime.get("Afternoon", 0.0)),
                    float(playtime.get("Evening", 0.0)), float(playtime.get("Night", 0.0))]
        except Exception as e:
            print(f"Error in playtimeByTimeOfDay: {e}")
            return [0.0, 0.0, 0.0, 0.0]

    @Property('QVariantList', notify=intervalChanged)
    def maxConsecutiveDays(self):
        try:
            streak, start_date, end_date = self.stats_service.get_max_consecutive_days(self._startDays, self._endDays)
            start_str = start_date.strftime('%d-%m-%Y') if start_date else ''
            end_str = end_date.strftime('%d-%m-%Y') if end_date else ''
            return [int(streak), start_str, end_str]
        except Exception as e:
            print(f"Error in maxConsecutiveDays: {e}")
            return [0, '', '']

    @Property('QVariantList', notify=intervalChanged)
    def topGames(self):
        try:
            result = self.stats_service.get_top_games(start_days=self._startDays, end_days=self._endDays, limit=5)
            return [[str(name), float(hours)] for name, hours in result]
        except Exception as e:
            print(f"Error in topGames: {e}")
            return []

    @Property('QVariantList', notify=intervalChanged)
    def pieChartData(self):
        try:
            games = self.stats_service.get_top_games(start_days=self._startDays, end_days=self._endDays)
            if not games:
                return [["No Data", 1.0]]

            total_hours = sum(hours for _, hours in games)
            if total_hours == 0:
                return [["No Data", 1.0]]

            games_sorted = sorted(games, key=lambda x: x[1], reverse=True)
            threshold = total_hours * 0.05
            major_games = []
            other_hours = 0

            for name, hours in games_sorted:
                if len(major_games) < 5 or hours >= threshold:
                    major_games.append([str(name), float(hours)])
                else:
                    other_hours += hours

            if other_hours > 0:
                if other_hours < total_hours * 0.05 and len(major_games) > 0:
                    major_games[-1][1] += other_hours
                    major_games[-1][0] += " and others"
                else:
                    major_games.append(["Other", float(other_hours)])

            return major_games if major_games else [["No Data", 1.0]]
        except Exception as e:
            print(f"Error in pieChartData: {e}")
            return [["No Data", 1.0]]
