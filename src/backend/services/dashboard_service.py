from datetime import datetime
from src.backend.repositories import *

class DashboardService:
    def __init__(self, db):
        self.game_stats_repo = GameStatsRepository(db)
        self.game_insights_repo = GameInsightsRepository(db)
        self.genre_stats_repo = GenreStatsRepository(db)
        self.release_year_stats_repo = ReleaseYearStatsRepository(db)
        self.streak_stats_repo = StreakStatsRepository(db)
        self.fun_facts_repo = FunFactsRepository(db)
        self.exp_stats_repo = ExpStatsRepository(db)

        '''
        self.time_stats_repo = TimeStatsRepository(db)
        self.session_stats_repo = SessionStatsRepository(db)
        self.day_stats_repo = DayStatsRepository(db)
        self.month_stats_repo = MonthStatsRepository(db)
        self.day_of_week_stats_repo = DayOfWeekStatsRepository(db)
        self.time_of_day_stats_repo = TimeOfDayStatsRepository(db)
        self.max_session_stats_repo = MaxSessionStatsRepository(db)
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
            'longest_gaming_day': self.game_stats_repo.get_longest_gaming_day_for_year(year),
        }

        # Добавляем инсайты по играм
        game_insights = {
            'game_of_the_year': self.game_insights_repo.get_game_of_the_year(year),
            'top3_games_percentage': self.game_insights_repo.get_top3_games_percentage(year),
            'new_releases_percentage': self.game_insights_repo.get_new_releases_percentage(year),
            'unique_games_count': self.game_insights_repo.get_unique_games_count(year)
        }
        stats.update(game_insights)

        # Добавляем инсайты по жанрам
        genre_insights = {
            'main_genre': self.genre_stats_repo.get_main_genre(year),
            'genre_distribution': self.genre_stats_repo.get_genre_distribution(year),
            'single_vs_multiplayer': self.genre_stats_repo.get_single_vs_multiplayer(year)
        }
        stats.update(genre_insights)

        # Добавляем инсайты по годам выпуска
        release_year_insights = {
            'playtime_by_release_year': self.release_year_stats_repo.get_playtime_by_release_year(year),
            'oldest_game_played': self.release_year_stats_repo.get_oldest_game_played(year)
        }
        stats.update(release_year_insights)

        # Добавляем данные о стриках
        streak_insights = {
            'longest_gaming_streak': self.streak_stats_repo.get_longest_gaming_streak_in_year(year),
            'longest_game_streak': self.streak_stats_repo.get_longest_game_streak_in_year(year),
            'longest_break': self.streak_stats_repo.get_longest_break_in_year(year)
        }
        stats.update(streak_insights)

        fun_facts = {
            'platform_distribution': self.fun_facts_repo.get_platform_distribution(year),
            'games_played_one_day': self.fun_facts_repo.get_games_played_one_day(year)
        }
        stats.update(fun_facts)

        exp_stats = {
            'overplayed_time_stats': self.exp_stats_repo.get_overplayed_time_percentage_in_year(year)
        }
        stats.update(exp_stats)

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
            'unique_games_count': str(stats['unique_games_count']),
            'main_genre': f"{stats['main_genre']['genre']}: {stats['main_genre']['hours']} hours" if stats['main_genre'] else "N/A",
            'genre_distribution': ', '.join([f"{g['genre']}: {g['percentage']}%" for g in stats['genre_distribution']]) if stats['genre_distribution'] else "N/A",
            'single_vs_multiplayer': f"Singleplayer: {stats['single_vs_multiplayer']['singleplayer']}%, Multiplayer: {stats['single_vs_multiplayer']['multiplayer']}%" if stats['single_vs_multiplayer'] else "N/A",
            'playtime_by_release_year': f"{year}: {stats['playtime_by_release_year']['selected_year']}%, {year-1}: {stats['playtime_by_release_year']['previous_year']}%, Older: {stats['playtime_by_release_year']['older_years']}%" if stats['playtime_by_release_year'] else "N/A",
            'oldest_game_played': f"{stats['oldest_game_played']['alias']} ({stats['oldest_game_played']['year']})" if stats['oldest_game_played'] else "N/A",
            'longest_gaming_streak': f"{stats['longest_gaming_streak']['length']} days, from {stats['longest_gaming_streak']['start_date']} to {stats['longest_gaming_streak']['end_date']}" if stats['longest_gaming_streak']['length'] > 0 else "N/A",
            'longest_game_streak': f"{stats['longest_game_streak']['game']} - {stats['longest_game_streak']['length']} days, from {stats['longest_game_streak']['start_date']} to {stats['longest_game_streak']['end_date']}" if stats['longest_game_streak']['length'] > 0 else "N/A",
            'longest_break': f"{stats['longest_break']['length']} days, from {stats['longest_break']['start_date']} to {stats['longest_break']['end_date']}" if stats['longest_break']['length'] > 0 else "N/A",
            'platform_distribution': f"Xbox: {stats['platform_distribution']['xbox']}%, Steam: {stats['platform_distribution']['steam']}%, Other: {stats['platform_distribution']['other']}%" if stats['platform_distribution'] else "N/A",
            'games_played_one_day': f"Total: {len(stats['games_played_one_day'][0])} games - {', '.join(stats['games_played_one_day'][0])}" if stats['games_played_one_day'] and stats['games_played_one_day'][0] else "N/A",
            'overplayed_time_stats': f"{stats['overplayed_time_stats']['percentage']}% ({stats['overplayed_time_stats']['overplayed_count']} sessions)" if stats['overplayed_time_stats'] else "N/A"
        }

        return formatted_stats
