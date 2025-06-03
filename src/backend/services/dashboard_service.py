from datetime import datetime
from src.backend.repositories import *

class DashboardService:
    def __init__(self, db):
        self.time_stats_repo = TimeStatsRepository(db)
        self.session_stats_repo = SessionStatsRepository(db)
        self.day_stats_repo = DayStatsRepository(db)
        self.month_stats_repo = MonthStatsRepository(db)
        self.day_of_week_stats_repo = DayOfWeekStatsRepository(db)
        self.time_of_day_stats_repo = TimeOfDayStatsRepository(db)
        self.max_session_stats_repo = MaxSessionStatsRepository(db)
        self.game_stats_repo = GameStatsRepository(db)
        self.genre_stats_repo = GenreStatsRepository(db)
        self.release_year_stats_repo = ReleaseYearStatsRepository(db)
        self.streak_stats_repo = StreakStatsRepository(db)
        self.platform_stats_repo = PlatformStatsRepository(db)
        self.overplayed_stats_repo = OverplayedStatsRepository(db)

    def get_total_playtime_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_playtime_percentage_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_session_count_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_average_session_duration_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_active_days_percentage_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_most_active_month_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_least_active_month_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_most_active_day_of_week_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_most_active_time_of_day_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_longest_gaming_day_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_game_of_the_year(self, year, start_days=None, end_days=None):
        pass

    def get_top_3_games_playtime_percentage_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_playtime_in_year_releases_percentage(self, year, start_days=None, end_days=None):
        pass

    def get_unique_game_count_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_main_genre_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_genre_distribution_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_single_vs_multiplayer_percentage_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_playtime_by_release_year_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_oldest_game_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_playtime_in_current_year_games_percentage(self, year, start_days=None, end_days=None):
        pass

    def get_longest_gaming_streak_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_longest_game_streak_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_longest_break_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_playtime_by_platform_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_single_day_games_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_overplayed_time_percentage_in_year(self, year, start_days=None, end_days=None):
        pass
