from plabtiercheck_app.models import StandardDataSource


def get_game_type_display(game_type_code):
    game_types = dict(StandardDataSource.GAME_TYPES)
    return game_types.get(game_type_code, "Unknown")
