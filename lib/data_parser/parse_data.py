import json
import pprint
import itertools
from typing import Optional, List

from lib.data_classes.tanks_stats import TankStats
from lib.data_classes.api_data import PlayerGlobalData
from lib.data_classes.session import SesionDiffData
from lib.exceptions import data_parser
from lib.logger import logger
import traceback

_log = logger.get_logger(__name__, 'DataParserLogger', 'logs/data_parser.log')


def get_normalized_data(data: PlayerGlobalData) -> PlayerGlobalData:
    try:
        all_stats = data.data.statistics.all

        data.data.statistics.all.avg_xp = all_stats.xp // all_stats.battles
        data.data.statistics.all.avg_damage = all_stats.damage_dealt // all_stats.battles
        data.data.statistics.all.accuracy = (all_stats.hits / all_stats.shots) * 100
        data.data.statistics.all.winrate = (all_stats.wins / all_stats.battles) * 100
        data.data.statistics.all.avg_spotted = all_stats.spotted / all_stats.battles
        data.data.statistics.all.frags_per_battle = all_stats.frags / all_stats.battles
        data.data.statistics.all.not_survived_battles = all_stats.battles - all_stats.survived_battles
        data.data.statistics.all.survival_ratio = (all_stats.survived_battles / all_stats.battles)
        data.data.statistics.all.damage_ratio = (all_stats.damage_dealt / all_stats.damage_received)
        data.data.statistics.all.destruction_ratio = (all_stats.frags / all_stats.not_survived_battles)

        data.data.statistics.rating.rating = 0

        if data.data.statistics.rating.calibration_battles_left == 0:
            data.data.statistics.rating.rating = round(data.data.statistics.rating.mm_rating * 10 + 3000)

        if data.data.statistics.rating.battles != 0:
            data.data.statistics.rating.winrate = (data.data.statistics.rating.wins / data.data.statistics.rating.battles)*100
        else:
            data.data.statistics.rating.winrate = 0
            
        if data.data.clan_stats is not None:
            data.data.name_and_tag = f'{data.nickname} [{data.data.clan_stats.tag}]'
        else:
            data.data.name_and_tag = f'{data.nickname}'

        if data.data.achievements.mainGun is None:
            data.data.achievements.mainGun = 0
        if data.data.achievements.markOfMastery is None:
            data.data.achievements.markOfMastery = 0
        if data.data.achievements.medalKolobanov is None:
            data.data.achievements.medalKolobanov = 0
        if data.data.achievements.medalRadleyWalters is None:
            data.data.achievements.medalRadleyWalters = 0
        if data.data.achievements.warrior is None:
            data.data.achievements.warrior = 0

        tanks = data.data.tank_stats

        for _, (key, tank) in enumerate(tanks.items()):

            if tank.all.battles != 0:
                tank.all.winrate = (tank.all.wins / tank.all.battles) * 100
                tank.all.avg_damage = tank.all.damage_dealt // tank.all.battles
            else:
                tank.all.winrate = 0
                tank.all.avg_damage = 0

            tanks[key] = tank
            
    except* (AttributeError, TypeError):
        _log.error(f'Data parsing error, \n{traceback.format_exc()}')
        raise data_parser.DataParserError()
    else:
        _log.debug('Parsing data: OK')
        return data
    
def get_session_stats(data_old: PlayerGlobalData, data_new: PlayerGlobalData) -> SesionDiffData:
    '''
    Return stats difference
    '''
    try:
        tank_ids = _sort_tanks_by_diff_battles(data_old, data_new)

        if tank_ids is None:
            _log.debug('Different data generating error: player data not updated')
            raise data_parser.NoDiffData('Different data generating error: player data not updated')

        battles_not_updated = False

        new_tank = None
        old_tank = None
        
        for _, (_, tank) in enumerate(data_old.data.tank_stats.items()):
            if tank.tank_id == tank_ids[0]:
                old_tank = tank
                break

        for _, (_, tank) in enumerate(data_new.data.tank_stats.items()):
            if tank.tank_id == tank_ids[0]:
                new_tank = tank
                break

        if old_tank is None or new_tank is None:
            _log.debug('Different data generating error: tank data not updated')
            raise data_parser.NoDiffData('Different data generating error: tank data not updated')

        data_new_shorted = data_new.data.statistics
        data_old_shorted = data_old.data.statistics

        r_diff_battles = data_new_shorted.rating.battles - data_old_shorted.rating.battles
        r_diff_rating = data_new_shorted.rating.rating - data_old_shorted.rating.rating
        r_diff_winrate = data_new_shorted.rating.winrate - data_old_shorted.rating.winrate

        if r_diff_battles != 0:
            r_session_winrate = data_new_shorted.rating.wins / data_new_shorted.rating.battles * 100
            r_session_rating = (data_new_shorted.rating.mm_rating - data_old_shorted.rating.mm_rating) * 10
        else:
            r_session_winrate = 0
            r_session_rating = 0
        
        if not battles_not_updated:
            diff_battles = data_new_shorted.all.battles - data_old_shorted.all.battles
            diff_winrate = data_new_shorted.all.winrate - data_old_shorted.all.winrate
            diff_avg_damage = data_new_shorted.all.avg_damage - data_old_shorted.all.avg_damage

            t_diff_battles = new_tank.all.battles - old_tank.all.battles
            
            if old_tank.all.battles != 0:
                old_tank.all.winrate = old_tank.all.wins / old_tank.all.battles * 100
                old_tank.all.avg_damage = old_tank.all.damage_dealt // old_tank.all.battles
            else:
                old_tank.all.winrate = 0
                old_tank.all.avg_damage = 0

            new_tank.all.winrate = new_tank.all.wins / new_tank.all.battles * 100
            t_diff_winrate = new_tank.all.winrate - old_tank.all.winrate
            
            t_diff_avg_damage = new_tank.all.avg_damage - old_tank.all.avg_damage

            if diff_battles > 0:
                session_winrate = (data_new_shorted.all.wins - data_old_shorted.all.wins) / diff_battles * 100
                session_avg_damage = new_tank.all.avg_damage - old_tank.all.avg_damage
                t_session_avg_damage =  (new_tank.all.damage_dealt - old_tank.all.damage_dealt) // t_diff_battles
            else:
                session_winrate = 0
                session_avg_damage = 0
                t_session_avg_damage = 0

            if new_tank.all.wins - old_tank.all.wins != 0:
                t_session_winrate = (new_tank.all.wins - old_tank.all.wins) / t_diff_battles * 100
            else:
                t_session_winrate = 0

            diff_data_dict = {
                'main_diff' : {
                    'winrate': diff_winrate,
                    'avg_damage': diff_avg_damage,
                    'battles': diff_battles
                },

                'main_session' : {
                    'winrate': session_winrate,
                    'avg_damage': session_avg_damage,
                    'battles': diff_battles
                },

                'rating_diff' : {
                    'winrate' : r_diff_winrate,
                    'rating' : r_diff_rating,
                    'battles' : r_diff_battles
                },

                'rating_session' : {
                    'winrate' : r_session_winrate,
                    'rating' : round(r_session_rating),
                    'battles' : r_diff_battles
                },

                'tank_diff' : {
                    'winrate' : t_diff_winrate,
                    'avg_damage' : t_diff_avg_damage,
                    'battles' : t_diff_battles
                },

                'tank_session' : {
                    'winrate' : t_session_winrate,
                    'avg_damage' : t_session_avg_damage,
                    'battles' : t_diff_battles
                },

                'tank_id' : tank_ids
            }

        else:
            _log.debug('Different data generating error: player data not updated')
            raise data_parser.NoDiffData('Different data generating error: player data not updated')

    except KeyError as e:
        raise data_parser.DataParserError(e)

    else:
        return SesionDiffData.model_validate(diff_data_dict)
    
def _get_index(tanks_list: List[TankStats], target: int): 
    for index, x in enumerate(tanks_list): 
        if x.tank_id == target: 
            return index
    return None

def _sort_tanks_by_diff_battles(data_old: PlayerGlobalData, data_new: PlayerGlobalData) -> Optional[List[str]]:
    if not isinstance(data_old, PlayerGlobalData) or not isinstance(data_new, PlayerGlobalData):
        raise ValueError('Wrong data type')
    
    tanks = data_new.data.tank_stats
    tanks_old = data_old.data.tank_stats

    diff_battles = []

    for _, (keys, tank) in enumerate(tanks.items()):
        try:
            diff = tank.all.battles - tanks_old[keys].all.battles
        except KeyError:
            continue
        else:
            if diff > 0:
                diff_battles.append([tank.tank_id, diff])

    if len(diff_battles) == 0:
        return None
    else:
        diff_battles = sorted(diff_battles, key=lambda x: x[1], reverse=True)
        diff_tank_id = list(map(lambda x: x[0], diff_battles))
        return diff_tank_id
    