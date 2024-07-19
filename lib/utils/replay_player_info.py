from lib.data_classes.replay_data_parsed import PlayerResult

def formatted_player_info(data: PlayerResult) -> str:
    clan_tag = f'| [{data.player_info.clan_tag}]' if data.player_info.clan_tag else ''
    return f'{data.player_info.nickname} {clan_tag}'
