from plabtiercheck_app.models import StandardDataSource, Player_info


def get_game_type_display(game_type_code):
    game_types = dict(StandardDataSource.GAME_TYPES)
    return game_types.get(game_type_code, "Unknown")

#
def get_tier_display(tier_code):
    player_tier = dict(Player_info.PLAYER_TIER_TYPE)
    return player_tier.get(tier_code, "Unknown")