from src.backend.repositories import *

class StatsService:
    def __init__(self, db):
        self.time_stats_repo = TimeStatsRepository(db)
        self.metadata_repo = MetadataRepository(db)
        self.app_repo = AppRepository(db)
        self.session_count_repo = SessionCountRepository(db)
        self.day_repo = DayRepository(db)
        self.max_session_repo = MaxSessionRepository(db)
        self.day_of_week_repo = DayOfWeekRepository(db)
        self.time_of_day_repo = TimeOfDayRepository(db)
        self.consecutive_days_repo = ConsecutiveDaysRepository(db)

    def get_full_total_playtime(self, start_days=None, end_days=None):
        total_seconds = self.time_stats_repo.get_full_total_seconds(start_days, end_days)
        return total_seconds / 3600.0

    def get_simp_total_playtime(self, start_days=None, end_days=None):
        total_seconds = self.time_stats_repo.get_simp_total_seconds(start_days, end_days)
        return total_seconds / 3600.0

    def get_top_games(self, start_days=None, end_days=None, limit=None):
        return self.app_repo.get_top_games(start_days, end_days, limit)

    def get_tracking_start_date(self):
        return self.metadata_repo.get_tracking_start_date()

    def get_max_interval_days(self):
        return self.metadata_repo.get_max_interval_days()

    def get_active_days_count(self, start_days=None, end_days=None):
        return self.day_repo.get_active_days_count(start_days, end_days)

    def get_full_session_count(self, start_days=None, end_days=None):
        return self.session_count_repo.get_full_session_count(start_days, end_days)

    def get_simp_session_count(self, start_days=None, end_days=None):
        return self.session_count_repo.get_simp_session_count(start_days, end_days)

    def get_avg_interval_playtime(self, start_days=None, end_days=None):
        simp_count = self.get_simp_session_count(start_days, end_days)
        if simp_count == 0:
            return 0.0  # Избегаем деления на 0
        avg_simp_time = self.get_simp_total_playtime(start_days, end_days) / simp_count
        return round(avg_simp_time, 2)  # Округляем до 2 знаков

    def get_avg_day_playtime(self, start_days=None, end_days=None):
        simp_total_seconds = self.time_stats_repo.get_simp_total_seconds(start_days, end_days)
        active_days = self.get_active_days_count(start_days, end_days)
        if active_days == 0:
            return 0.0
        return (simp_total_seconds / 3600.0) / active_days

    def get_max_session_duration(self, start_days=None, end_days=None):
        duration, game_name, date = self.max_session_repo.get_max_session_duration(start_days, end_days)
        return (duration, game_name, date)

    def get_max_daily_game_session(self, start_days=None, end_days=None):
        duration, date, game_name, session_count = self.max_session_repo.get_max_daily_game_session(start_days,
                                                                                                    end_days)
        return (duration, date, game_name, session_count)

    def get_max_daily_total_duration(self, start_days=None, end_days=None):
        duration, date, game_details = self.max_session_repo.get_max_daily_total_duration(start_days, end_days)
        return (duration, date, game_details)

    def get_playtime_by_day_of_week(self, start_days=None, end_days=None):
        return self.day_of_week_repo.get_playtime_by_day_of_week(start_days, end_days)

    def get_playtime_by_time_of_day(self, start_days=None, end_days=None):
        return self.time_of_day_repo.get_playtime_by_time_of_day(start_days, end_days)

    def get_max_consecutive_days(self, start_days=None, end_days=None):
        streak, start_date, end_date = self.consecutive_days_repo.get_max_consecutive_days(start_days, end_days)
        return (streak, start_date, end_date)

    def get_games_list(self):
        return self.app_repo.get_games_list()

    def update_game_metadata(self, app_id, icon_path, genre, year):
        """Обновляет метаданные игры через AppRepository."""
        self.app_repo.update_game_metadata(app_id, icon_path, genre, year)




