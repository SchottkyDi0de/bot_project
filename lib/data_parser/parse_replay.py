import json
import asyncio
import traceback
from enum import Enum

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

for i, map in enumerate(Maps):
    print(map.name, map.value)

class ParseReplayData:
    def __init__(self):
        self.api = API()

    def parse(self, data: ReplayData, region: str) -> ParsedReplayData:
        try:
            parsed_data = ParsedReplayData.model_validate(data.model_dump())
            # get all players ids
            players_ids = []
            for player in data.players:
                players_ids.append(player.account_id)

            _log.debug(f'len {len(players_ids)}')

            # get all players stats
            players_stats = asyncio.run(self.api.get_players_stats(players_ids, region))
            for i in players_stats:
                pass
                _log.debug(json.dumps(i.to_dict(), indent=4))
                for player_stats in players_stats:
                    parsed_data.player_results[players_stats.index(player_stats)].statistics = player_stats
            
            for player_result in parsed_data.player_results:
                if player_result.statistics is not None:
                    if player_result.statistics.all.battles > 0:
                        player_result.statistics.all.winrate = (
                            player_result.statistics.all.wins / 
                            player_result.statistics.all.battles
                            ) * 100
                    else:
                        player_result.statistics.all.winrate = 0.0

                parsed_data.player_results[parsed_data.player_results.index(player_result)] = player_result

            try:
                parsed_data.map_name = Maps(data.mode_map_id & 0xFFFF).name
            except ValueError:
                parsed_data.map_name = None
                    
            # # 
            # print(json.dumps(parsed_data.model_dump(), indent=4))

        except Exception:
            _log.error(f'Error while parsing replay data\n{traceback.format_exc()}')
            raise DataParserError('Error while parsing replay data')
        

def test():
    data = ReplayParser().parse('test.wotbreplay', False)
    parsed_replay_data = ParseReplayData().parse(data, 'eu')

test()