import json
import asyncio
import traceback
from enum import Enum
from datetime import datetime

from lib.api.async_wotb_api import API
from lib.data_classes.replay_data import ReplayData
from lib.data_classes.replay_data_parsed import ParsedReplayData
from lib.exceptions.data_parser import DataParserError
from lib.logger.logger import get_logger
from lib.replay_parser.parser import ReplayParser

_log = get_logger(__name__, 'ReplayParserLogger', 'logs/replay_parser.log')


class Maps(Enum):
    desert_sands = 2
    middleburg = 3
    copperfield = 4
    alpenstadt = 5
    mines = 6
    dead_rail = 7
    fort_despair = 8
    himmelsdorf = 9
    black_goldville = 10
    oasis_palms = 11
    ghost_factory = 12
    molendijk = 14
    port_bay = 15
    winter_malinovka = 19
    castilla = 20
    canal = 21
    vineyards = 23
    yamato_harbor = 25
    canyon = 27
    mayan_ruins = 30
    dynasty_pearl = 31
    naval_frontier = 35
    falls_creek = 38
    new_bay = 40
    normandy = 42
    wasteland = 71


class RoomType(Enum):
    any = 0
    regular = 1
    training_room = 2
    tournament = 4
    quick_tournament = 5
    rating = 7
    mad_games = 8
    realistic_battles = 22
    uprising = 23
    gravity_mode = 24
    skirmish = 25
    burning_games = 26


class ParseReplayData:
    def __init__(self):
        self.api = API()

    async def parse(self, data: ReplayData, region: str) -> ParsedReplayData:
        try:
            parsed_data = ParsedReplayData.model_validate(data.model_dump())

            # get all players ids
            players_ids = []
            for player in data.players:
                players_ids.append(player.account_id)
            
            # Set time in human readable format
            parsed_data.time_string = datetime.fromtimestamp(data.timestamp_secs).strftime("%d/%m/%Y\n%H:%M:%S | UTC + 0")

            # get all players stats
            players_stats = await self.api.get_players_stats(players_ids, region)
            
            for player_stats in players_stats:
                if not isinstance(player_stats, bool):
                    for player_result in parsed_data.player_results:
                        if player_stats.data.account_id == player_result.info.account_id:
                            player_result.statistics = player_stats.data.statistics     
        
            for player_result in parsed_data.player_results:
                if player_result.statistics is not None:
                    if player_result.statistics.all.battles > 0:
                        player_result.statistics.all.winrate = (
                            player_result.statistics.all.wins / 
                            player_result.statistics.all.battles
                            ) * 100
                    else:
                        player_result.statistics.all.winrate = 0.0

            for player in data.player_results:
                if parsed_data.author.account_id == player.info.account_id:
                    parsed_data.author.tank_id = player.info.tank_id

            for player_result in parsed_data.player_results:
                for player in parsed_data.players:
                    if player.account_id == player_result.info.account_id:
                        player_result.player_info = player.info
                        parsed_data.player_results[parsed_data.player_results.index(player_result)] = player_result

            try:
                parsed_data.map_name = Maps(data.mode_map_id & 0xFFFF).name
            except ValueError:
                _log.debug(f'Map is not defined, map_id {data.mode_map_id & 0xFFFF}')

            try:
                parsed_data.room_name = RoomType(data.room_type).name
            except ValueError:
                _log.debug(f'Room type is not defined, room_type {data.room_type}')

            if parsed_data.author.team_number == parsed_data.winner_team_number:
                parsed_data.author.winner = True
            else:
                parsed_data.author.winner = False

            if parsed_data.author.n_shots > 0:
                parsed_data.author.accuracy = parsed_data.author.n_hits / parsed_data.author.n_shots * 100
                parsed_data.author.penertarions_percent = parsed_data.author.n_penetrations / parsed_data.author.n_shots * 100
            
            return parsed_data
            # print(json.dumps(parsed_data.model_dump(), indent=4))

        except Exception:
            _log.error(f'Error while parsing replay data\n{traceback.format_exc()}')
            raise DataParserError('Error while parsing replay data')
        

# def test():
#     data = ReplayParser().parse('test.wotbreplay', False)
#     parsed_replay_data = ParseReplayData().parse(data, 'eu')

# test()
