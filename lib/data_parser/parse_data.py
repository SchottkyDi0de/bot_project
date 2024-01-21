import json
import pprint
import itertools
from typing import Optional, List

from lib.data_classes.tanks_stats import TankStats
from lib.database.tankopedia import TanksDB
from lib.data_classes.session import TankSessionData
from lib.data_classes.api_data import PlayerGlobalData
from lib.data_classes.session import SessionDiffData
from lib.exceptions import data_parser
from lib.logger import logger
import traceback

_log = logger.get_logger(__name__, 'DataParserLogger', 'logs/data_parser.log')
_tdb = TanksDB()

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
        return data
    
def get_session_stats(data_old: PlayerGlobalData, data_new: PlayerGlobalData) -> SessionDiffData:
    '''
    Return stats difference
    '''
    try:
        tank_stats = _generate_tank_session_list(data_old, data_new)
        battles_not_updated = True if tank_stats is None else False

        data_new_shorted = data_new.data.statistics
        data_old_shorted = data_old.data.statistics

        r_diff_battles = data_new_shorted.rating.battles - data_old_shorted.rating.battles
        r_diff_rating = data_new_shorted.rating.rating - data_old_shorted.rating.rating
        r_diff_winrate = data_new_shorted.rating.winrate - data_old_shorted.rating.winrate

        if r_diff_battles != 0:
            r_session_winrate = (data_new_shorted.rating.wins - data_old_shorted.rating.wins) / r_diff_battles * 100
            r_session_rating = (data_new_shorted.rating.mm_rating - data_old_shorted.rating.mm_rating) * 10 + 3000
        else:
            r_session_winrate = 0
            r_session_rating = 0

        if not battles_not_updated:
            diff_battles = data_new_shorted.all.battles - data_old_shorted.all.battles
            diff_winrate = data_new_shorted.all.winrate - data_old_shorted.all.winrate
            diff_avg_damage = data_new_shorted.all.avg_damage - data_old_shorted.all.avg_damage

            if diff_battles > 0:
                session_winrate = (data_new_shorted.all.wins - data_old_shorted.all.wins) / diff_battles * 100
                session_avg_damage = (data_new_shorted.all.damage_dealt - data_old_shorted.all.damage_dealt) // diff_battles
            else:
                session_winrate = 0
                session_avg_damage = 0

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
                'tank_stats' : tank_stats,
                'tank_ids' : [tank.tank_id for tank in tank_stats] if tank_stats is not None else None
            }
            _log.debug(f'Tank ids: {diff_data_dict["tank_ids"]}')

        else:
            _log.debug('Different data generating error: player data not updated')
            raise data_parser.NoDiffData('Different data generating error: player data not updated')

    except KeyError as e:
        raise data_parser.DataParserError(e)

    else:
        return SessionDiffData.model_validate(diff_data_dict)

def _generate_tank_session_list(data_old: PlayerGlobalData, data_new: PlayerGlobalData) -> Optional[List[TankSessionData]]:
    if not isinstance(data_old, PlayerGlobalData) or not isinstance(data_new, PlayerGlobalData):
        raise TypeError('Wrong data type, expected PlayerGlobalData for both data_old and data_new')

    tanks = data_new.data.tank_stats
    tanks_old = data_old.data.tank_stats

    diff_battles = []

    for _, (key, tank) in enumerate(tanks.items()):
        tank_stats: list = []
        try:
            diff = tank.all.battles - tanks_old[key].all.battles
            # _log.debug(f'compare tanks battles {key}: {tank.all.battles} - {tanks_old[key].all.battles} = {diff}')
        except KeyError:
            continue
        else:
            if diff > 0:
                diff_battles.append([tank.tank_id, diff])

    _log.debug(f'Len diff_battles: {len(diff_battles)}')
    if len(diff_battles) == 0:
        _log.debug('No tanks in diff_battles')
        return None
    else:
        diff_battles = sorted(diff_battles, key=lambda x: x[1], reverse=True)
        diff_tank_id = list(map(lambda x: x[0], diff_battles))
    
    for tank_id in diff_tank_id:
        tank_id = str(tank_id)
        db_tank = _tdb.safe_get_tank_by_id(tank_id)
        
        if not db_tank is None:
            tank_name = db_tank['name']
            tank_tier = db_tank['tier']
            tank_type = db_tank['type']
        else:
            tank_type = 'Unknown'
            tank_name = 'Unknown'
            tank_tier = 0
        
        tank_diff_battles = tanks[tank_id].all.battles - tanks_old[tank_id].all.battles
        
        if tank_diff_battles == 0:
            continue

        d_winrate = tanks[tank_id].all.winrate - tanks_old[tank_id].all.winrate
        d_avg_damage = tanks[tank_id].all.avg_damage - tanks_old[tank_id].all.avg_damage

        s_avg_damage: int = (tanks[tank_id].all.damage_dealt - tanks_old[tank_id].all.damage_dealt) // tank_diff_battles
        s_winrate: float = (tanks[tank_id].all.wins - tanks_old[tank_id].all.wins) / tank_diff_battles * 100

        tank_stats.append(
            TankSessionData.model_validate(
                {
                'tank_name': tank_name,
                'tank_tier': tank_tier,
                'tank_type': tank_type,
                'd_winrate': d_winrate,
                'd_avg_damage': d_avg_damage,
                'd_battles': tank_diff_battles,
                's_winrate': s_winrate,
                's_avg_damage': s_avg_damage,
                's_battles': tank_diff_battles,
                'tank_id' : int(tank_id)
                }
            )
        )
    return tank_stats

        
