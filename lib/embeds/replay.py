from discord import Embed
from discord.ext.commands import Context

from lib.locale.locale import Text
from lib.data_classes.replay_data_parsed import \
    ParsedReplayData, PlayerResult, Statistics
from lib.utils.string_parser import insert_data
from lib.logger.logger import get_logger
from lib.database.tankopedia import TanksDB
from lib.exceptions.database import TankNotFoundInTankopedia

_log = get_logger(__name__, 'EmbedReplayBuilder', 'logs/embed_replay.log')

class EmbedReplayBuilder():
    def __init__(self):
        self.embed = None
        self.text = Text().get()
        self.tanks_db = TanksDB()

    def get_tank_name(self, tank_id: int) -> str:
        try:
            tank = self.tanks_db.get_tank_by_id(tank_id)
        except TankNotFoundInTankopedia:
            _log.debug(f'Tank with id {tank_id} not found')
            return 'Unknown'
        else:
            return tank['name']
        
    def get_tank_tier(self, tank_id: int) -> str:
        try:
            tank = self.tanks_db.get_tank_by_id(tank_id)
        except TankNotFoundInTankopedia:
            _log.debug(f'Tank with id {tank_id} not found')
            return '?'
        else:
            return str(tank['tier'])

    def string_len_handler(self, string: str, length: int) -> str:
        len_diff = length - len(string)
        if len_diff > 0:
            return string + (' ' * len_diff)
        else:
            return string

    def num_cutter(self, value: int) -> str:
        if value > 99_999:
            return str(round(value / 1000, 2)) + 'k'
        else:
            return str(value)

    def nickname_cutter(self, nickname: str, max_len: int = 11) -> str:
        return (nickname[:max_len] + '..') if len(nickname) > max_len else nickname
    
    def avg_stats_counter(self, data: ParsedReplayData, enemies: bool) -> str:
        team = data.author.team_number
        avg_stats: str = ''
        avg_battles = 0
        avg_winrate = 0.0
        player_stats: list[Statistics] = []

        for player in data.player_results:
            if enemies:
                if player.player_info.team != team:
                    if player.statistics:
                        player_stats.append(player.statistics)
            else:
                if player.player_info.team == team:
                    if player.statistics:
                        player_stats.append(player.statistics)

        if len(player_stats) > 0:
            avg_battles = round(sum(statistics.all.battles for statistics in player_stats) / len(player_stats))
            avg_winrate = round(sum(statistics.all.winrate for statistics in player_stats) / len(player_stats), 1)
        
        avg_stats = (
            self.string_len_handler(
                self.nickname_cutter(
                    self.text.cmds.parse_replay.items.avg_stats,
                ),
                length=15
            )+\
            self.string_len_handler(
                str(avg_winrate),
                length=5
            )+\
            self.num_cutter(avg_battles)+'\n'+('.'*25)+'\n'
        )
        return avg_stats
    
    def get_map_name(self, map: str):
        try:
            return getattr(self.text.map_names, map)
        except AttributeError:
            return self.text.map_names.unknown
        
    def get_room_name(self, room: str):
        try:
            return getattr(self.text.gamemodes, room)
        except AttributeError:
            return self.text.gamemodes.unknown


    def gen_players_list(self, data: ParsedReplayData, enemies: bool) -> str:
        team = data.author.team_number
        players: list[PlayerResult] = []
        players_str = ''

        for player in data.player_results:
            if enemies:
                if player.player_info.team != team:
                    players.append(player)
            else:
                if player.player_info.team == team:
                    players.append(player)

        for enemy in players:
            if enemy.statistics:
                nickname = self.string_len_handler(
                    self.nickname_cutter(
                        enemy.player_info.nickname,
                    ),
                    15
                )
                winrate = self.string_len_handler(
                    str(round(enemy.statistics.all.winrate, 1)),
                    5
                )
                battles = self.num_cutter(enemy.statistics.all.battles)
                players_str += f'{nickname}{winrate}{battles}\n'
            else:
                players_str += f'{self.text.cmds.parse_replay.items.empty_player}\n'
        
        return players_str

    def build_embed(self, ctx: Context, data: ParsedReplayData) -> Embed:
        author_id = data.author.account_id

        for player_result in data.player_results:
            if player_result.info.account_id == author_id:
                author_stats = player_result

        self.embed = Embed(
            title=insert_data(
                self.text.cmds.parse_replay.items.title, 
                ('member_id', 'nickname'),
                (str(ctx.author.name), str(author_stats.player_info.nickname))
            ),
            description=insert_data(
                self.text.cmds.parse_replay.items.description,
                (
                    'battle_result',
                    'battle_type',
                    'tank_name',
                    'tier',
                    'map',
                    'time',
                    'damage_dealt',
                    'damage_assisted',
                    'damage_blocked',
                    'point_captured',
                    'point_defended',
                    'shots_fired',
                    'shots_hit',
                    'shots_penetrated',
                    'accuracy',
                    'penetration',
                    'allies',
                    'enemies'
                ),
                (
                    self.text.cmds.parse_replay.items.common.win if data.author.winner \
                        else self.text.cmds.parse_replay.items.common.lose,
                    self.get_map_name(data.room_name),
                    self.get_tank_name(data.author.tank_id),
                    self.get_tank_tier(data.author.tank_id),
                    self.get_map_name(data.map_name),
                    str(data.time_string),
                    str(author_stats.info.damage_dealt),
                    str(author_stats.info.damage_assisted_1),
                    str(author_stats.info.damage_blocked),
                    str(author_stats.info.victory_points_earned),
                    str(author_stats.info.victory_points_seized),
                    str(author_stats.info.n_shots),
                    str(author_stats.info.n_hits_dealt),
                    str(author_stats.info.n_penetrations_dealt),
                    str(round(data.author.accuracy, 2)),
                    str(round(data.author.penertarions_percent, 2)),
                    self.avg_stats_counter(data, False)+\
                        self.gen_players_list(data, False),
                    self.avg_stats_counter(data, True)+\
                        self.gen_players_list(data, True)
                )
            )
        )
        return self.embed