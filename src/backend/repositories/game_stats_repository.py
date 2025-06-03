class GameStatsRepository:
    def __init__(self, db):
        self.db = db

    def get_game_of_the_year(self, year, start_days=None, end_days=None):
        pass

    def get_top_3_games_playtime_in_year(self, year, start_days=None, end_days=None):
        pass

    def get_playtime_in_year_releases(self, year, start_days=None, end_days=None):
        pass

    def get_unique_game_count_in_year(self, year, start_days=None, end_days=None):
        pass
