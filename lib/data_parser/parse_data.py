from lib.data_classes.api_data import PlayerGlobalData
from lib.data_classes.session import SesionDiffData
from lib.database import tankopedia
from lib.exceptions import data_parser
from lib.logger import logger
from lib.yaml.yaml2object import Parser

_log = logger.get_logger(__name__, 'DataParserLogger', 'logs/data_parser.log')


def get_normalized_data(data: PlayerGlobalData) -> PlayerGlobalData:
    try:
        all_stats = data.data.statistics.all

        data.data.statistics.all.avg_xp = all_stats.xp // all_stats.battles
        data.data.statistics.all.avg_damage = all_stats.damage_dealt // all_stats.battles
        data.data.statistics.all.accuracy = round((all_stats.hits / all_stats.shots) * 100, 2)
        data.data.statistics.all.winrate = round((all_stats.wins / all_stats.battles) * 100, 2)
        data.data.statistics.all.avg_spotted = round((all_stats.spotted / all_stats.battles), 2)
        data.data.statistics.all.frags_per_battle = round((all_stats.frags / all_stats.battles), 2)
        data.data.statistics.all.not_survived_battles = all_stats.battles - all_stats.survived_battles
        data.data.statistics.all.survival_ratio = round((all_stats.survived_battles / all_stats.battles), 2)
        data.data.statistics.all.damage_ratio = round((all_stats.damage_dealt / all_stats.damage_received), 2)
        data.data.statistics.all.destruction_ratio = round((all_stats.frags / all_stats.not_survived_battles), 2)

        data.data.statistics.rating.rating = 0

        if data.data.statistics.rating.calibration_battles_left == 0:
            data.data.statistics.rating.rating = round(data.data.statistics.rating.mm_rating * 10 + 3000)

        if data.data.statistics.rating.battles != 0:
            data.data.statistics.rating.winrate = round((data.data.statistics.rating.wins / data.data.statistics.rating.battles)*100, 2)
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

        for i, j in enumerate(tanks):
            tank = j

            if tank.all.battles != 0:
                tank.all.winrate = round((tank.all.wins / tank.all.battles) * 100, 2)
                tank.all.avg_damage = tank.all.damage_dealt // tank.all.battles
            else:
                tank.all.winrate = 0
            
            tanks.insert(i, tank)
            data.data.tank_stats.pop(i)
            data.data.tank_stats = tanks
            
    except Exception as e:
        _log.error(f'Data parsing error, {str(e)}')
        raise data_parser.DataParserError(e)
    else:
        _log.debug('Parsing data: OK')
        return data
    
def get_session_stats(data_old: PlayerGlobalData, data_new: PlayerGlobalData) -> SesionDiffData:
    '''
    Return stats difference
    '''
    try:
        tank_data = _search_max_diff_battles_tank(data_old, data_new)

        if tank_data is None:
            _log.debug('Different data generating error: player data not updated')
            raise data_parser.NoDiffData('Different data generating error: player data not updated')

        tank_id = tank_data[0]

        tank_index = tank_data[1]
        battles_not_updated = False
        
        for i in data_old.data.tank_stats:
            if i.tank_id == tank_id:
                old_tank = i
                break

        for i in data_new.data.tank_stats:
            if i.tank_id == tank_id:
                new_tank = i
                break

        data_new_shorted = data_new.data.statistics
        data_old_shorted = data_old.data.statistics

        r_diff_battles = data_new_shorted.rating.battles - data_old_shorted.rating.battles
        r_diff_rating = data_new_shorted.rating.rating - data_old_shorted.rating.rating
        r_diff_winrate = data_new_shorted.rating.winrate - data_old_shorted.rating.winrate

        if r_diff_battles != 0:
            r_session_winrate = round((data_new_shorted.rating.wins / data_new_shorted.rating.battles) * 100, 2)
            r_session_rating = (data_new_shorted.rating.mm_rating - data_old_shorted.rating.mm_rating) * 10
        else:
            r_session_winrate = 0
            r_session_rating = 0
        
        if not battles_not_updated:
            diff_battles = data_new_shorted.all.battles - data_old_shorted.all.battles
            diff_winrate = round(data_new_shorted.all.winrate - data_old_shorted.all.winrate, 2)
            diff_avg_damage = data_new_shorted.all.avg_damage - data_old_shorted.all.avg_damage

            t_diff_battles = new_tank.all.battles - old_tank.all.battles
            
            old_tank.all.winrate = round((old_tank.all.wins / old_tank.all.battles) * 100, 2)
            new_tank.all.winrate = round((new_tank.all.wins / new_tank.all.battles) * 100, 2)
            t_diff_winrate = new_tank.all.winrate - old_tank.all.winrate
            
            t_avg_damage_before = old_tank.all.damage_dealt // old_tank.all.battles
            t_avg_damage_after = new_tank.all.damage_dealt // new_tank.all.battles
            t_diff_avg_damage = t_avg_damage_after - t_avg_damage_before

            session_winrate = round((data_new_shorted.all.wins - data_old_shorted.all.wins) // diff_battles * 100, 2)
            session_avg_damage = (data_new_shorted.all.damage_dealt - data_old_shorted.all.damage_dealt) // diff_battles

            t_session_winrate = round((new_tank.all.wins - old_tank.all.wins) // t_diff_battles * 100, 2)
            t_session_avg_damage = (new_tank.all.damage_dealt - old_tank.all.damage_dealt) // t_diff_battles
            
            
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
                    'rating' : r_session_rating,
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

                'tank_id' : tank_id,
                'tank_index' : tank_index
            }

        else:
            _log.debug('Different data generating error: player data not updated')
            raise data_parser.NoDiffData('Different data generating error: player data not updated')

    except KeyError as e:
        raise data_parser.DataParserError(e)

    else:
        return SesionDiffData(diff_data_dict)

def _search_max_diff_battles_tank(data_old: PlayerGlobalData, data_new: PlayerGlobalData) -> tuple[int, int]:
    max_diff_battles = 0
    max_tank_id = None
    tanks = data_new.data.tank_stats
    tanks_old = data_old.data.tank_stats

    for i, j in enumerate(tanks):
        try:
            battles_before = tanks_old[i].all.battles
            battles_after = tanks[i].all.battles
            diff_battles = battles_after - battles_before
        except IndexError:
            continue

        if diff_battles == 0:
            continue

        if diff_battles > max_diff_battles:
            max_diff_battles = diff_battles
            max_tank_id = j.tank_id
            tank_index = i

    if max_diff_battles == 0:
        return None
    else:
        return (max_tank_id, tank_index)
