from datetime import datetime
from src.backend.repositories import *

class DashboardService:
    def __init__(self, db):
        self.game_stats_repo = GameStatsRepository(db)
        self.game_insights_repo = GameInsightsRepository(db)

        '''
        self.time_stats_repo = TimeStatsRepository(db)
        self.session_stats_repo = SessionStatsRepository(db)
        self.day_stats_repo = DayStatsRepository(db)
        self.month_stats_repo = MonthStatsRepository(db)
        self.day_of_week_stats_repo = DayOfWeekStatsRepository(db)
        self.time_of_day_stats_repo = TimeOfDayStatsRepository(db)
        self.max_session_stats_repo = MaxSessionStatsRepository(db)
        self.genre_stats_repo = GenreStatsRepository(db)
        self.release_year_stats_repo = ReleaseYearStatsRepository(db)
        self.streak_stats_repo = StreakStatsRepository(db)
        self.platform_stats_repo = PlatformStatsRepository(db)
        self.overplayed_stats_repo = OverplayedStatsRepository(db)
        '''

    def get_unique_years(self):
        return self.game_stats_repo.get_unique_years()

    def get_year_stats(self, year):
        """Получаем все статистические данные для указанного года"""
        if not year:
            return None

        stats = {
            'total_playtime': self.game_stats_repo.get_total_playtime_for_year(year),
            'percentage_of_total': self.game_stats_repo.get_percentage_of_yearly_playtime(year),
            'session_count': self.game_stats_repo.get_session_count_for_year(year),
            'avg_session_duration': self.game_stats_repo.get_avg_session_duration_for_year(year),
            'active_days_percentage': self.game_stats_repo.get_active_days_percentage_for_year(year),
            'most_active_month': self.game_stats_repo.get_most_active_month_for_year(year),
            'least_active_month': self.game_stats_repo.get_least_active_month_for_year(year),
            'most_active_day_of_week': self.game_stats_repo.get_most_active_day_of_week_for_year(year),
            'most_active_time_of_day': self.game_stats_repo.get_most_active_time_of_day_for_year(year),
            'longest_gaming_day': self.game_stats_repo.get_longest_gaming_day_for_year(year)
        }

        # Добавляем инсайты по играм
        game_insights = {
            'game_of_the_year': self.game_insights_repo.get_game_of_the_year(year),
            'top3_games_percentage': self.game_insights_repo.get_top3_games_percentage(year),
            'new_releases_percentage': self.game_insights_repo.get_new_releases_percentage(year),
            'unique_games_count': self.game_insights_repo.get_unique_games_count(year)
        }
        stats.update(game_insights)

        # Форматируем данные для отображения
        formatted_stats = {
            'total_playtime': f"{stats['total_playtime']} hours",
            'percentage_of_total': f"{stats['percentage_of_total']}%",
            'session_count': str(stats['session_count']),
            'avg_session_duration': f"{stats['avg_session_duration']} hours",
            'active_days_percentage': f"{stats['active_days_percentage']}%",
            'most_active_month': f"{stats['most_active_month']['month']} ({stats['most_active_month']['hours']} hours)" if stats['most_active_month'] else "N/A",
            'least_active_month': f"{stats['least_active_month']['month']} ({stats['least_active_month']['hours']} hours)" if stats['least_active_month'] else "N/A",
            'most_active_day_of_week': f"{stats['most_active_day_of_week']['day']} ({stats['most_active_day_of_week']['hours']} hours)" if stats['most_active_day_of_week'] else "N/A",
            'most_active_time_of_day': f"{stats['most_active_time_of_day']['time_period']} ({stats['most_active_time_of_day']['hours']} hours)" if stats['most_active_time_of_day'] else "N/A",
            'longest_gaming_day': f"{stats['longest_gaming_day']['date']} ({stats['longest_gaming_day']['hours']} hours)" if stats['longest_gaming_day'] else "N/A",
            'game_of_the_year': f"{stats['game_of_the_year']['game']}: {stats['game_of_the_year']['hours']} hours" if stats['game_of_the_year'] else "N/A",
            'top3_games_percentage': f"{stats['top3_games_percentage']['percentage']}% in {', '.join([g['game'] for g in stats['top3_games_percentage']['games']])}" if stats['top3_games_percentage']['games'] else "N/A",
            'new_releases_percentage': f"{stats['new_releases_percentage']['percentage']}% in {', '.join([g['game'] for g in stats['new_releases_percentage']['games']])}" if stats['new_releases_percentage']['games'] else "N/A",
            'unique_games_count': str(stats['unique_games_count'])
        }

        return formatted_stats
