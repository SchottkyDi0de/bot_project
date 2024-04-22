import traceback

from lib.data_classes.api.api_data import PlayerGlobalData
from lib.data_classes.session import SessionDiffData, TankSessionData
from lib.database.tankopedia import TanksDB
from lib.exceptions import data_parser
from lib.logger import logger
from lib.utils.safe_divide import safe_divide

_log = logger.get_logger(__file__, 'DataParserLogger', 'logs/data_parser.log')
_tdb = TanksDB()

def get_normalized_data(data: PlayerGlobalData) -> PlayerGlobalData:
    try:
        all_stats = data.data.statistics.all
        rating_stats = data.data.statistics.rating

        data.data.statistics.all.avg_xp = all_stats.xp // all_stats.battles
        data.data.statistics.all.avg_damage = all_stats.damage_dealt // all_stats.battles
        data.data.statistics.all.accuracy = safe_divide(all_stats.hits, all_stats.shots) * 100
        data.data.statistics.all.winrate = (all_stats.wins / all_stats.battles) * 100
        data.data.statistics.all.avg_spotted = all_stats.spotted / all_stats.battles
        data.data.statistics.all.frags_per_battle = all_stats.frags / all_stats.battles
        data.data.statistics.all.not_survived_battles = all_stats.battles - all_stats.survived_battles
        data.data.statistics.all.survival_ratio = (all_stats.survived_battles / all_stats.battles)
        data.data.statistics.all.damage_ratio = safe_divide(all_stats.damage_dealt, all_stats.damage_received)
        data.data.statistics.all.destruction_ratio = safe_divide(all_stats.frags, all_stats.not_survived_battles)
        
        data.data.statistics.rating.avg_xp = rating_stats.xp // rating_stats.battles
        data.data.statistics.rating.avg_damage = rating_stats.damage_dealt // rating_stats.battles
        data.data.statistics.rating.accuracy = safe_divide(rating_stats.hits, rating_stats.shots) * 100
        data.data.statistics.rating.winrate = (rating_stats.wins / rating_stats.battles) * 100
        data.data.statistics.rating.avg_spotted = rating_stats.spotted / rating_stats.battles
        data.data.statistics.rating.frags_per_battle = rating_stats.frags / rating_stats.battles
        data.data.statistics.rating.not_survived_battles = rating_stats.battles - rating_stats.survived_battles
        data.data.statistics.rating.survival_ratio = (rating_stats.survived_battles / rating_stats.battles)
        data.data.statistics.rating.damage_ratio = safe_divide(rating_stats.damage_dealt, rating_stats.damage_received)
        data.data.statistics.rating.destruction_ratio = safe_divide(rating_stats.frags, rating_stats.not_survived_battles)

        if data.data.statistics.rating.calibration_battles_left == 0 and data.data.statistics.rating.battles != 0:
            data.data.statistics.rating.rating = round(data.data.statistics.rating.mm_rating * 10 + 3000)
        else:
            data.data.statistics.rating.rating = 0

        if data.data.statistics.rating.battles != 0:
            data.data.statistics.rating.winrate = (data.data.statistics.rating.wins / data.data.statistics.rating.battles) * 100
            data.data.statistics.rating.accuracy = safe_divide(data.data.statistics.rating.hits, data.data.statistics.rating.shots) * 100
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

        for key, tank in tanks.items():
            if tank.all.battles != 0:
                tank.all.winrate = (tank.all.wins / tank.all.battles) * 100
                tank.all.avg_damage = tank.all.damage_dealt // tank.all.battles
                tank.all.accuracy = safe_divide(tank.all.hits, tank.all.shots) * 100
                tank.all.damage_ratio = safe_divide(tank.all.damage_dealt, tank.all.damage_received)
                tank.all.destruction_ratio = safe_divide(
                    tank.all.frags, (tank.all.battles - tank.all.survived_battles)
                )
                tank.all.frags_per_battle = tank.all.frags / tank.all.battles
                tank.all.avg_spotted = tank.all.spotted / tank.all.battles
                tank.all.survival_ratio = tank.all.survived_battles / tank.all.battles
                tank.all.losses = tank.all.battles - tank.all.wins
            else:
                tank.all.winrate = 0.0
                tank.all.avg_damage = 0
                tank.all.accuracy = 0.0
                tank.all.damage_ratio = 0.0
                tank.all.losses = 0
                tank.all.destruction_ratio = 0.0
                tank.all.frags_per_battle = 0.0
                tank.all.avg_spotted = 0.0
                tank.all.survival_ratio = 0.0

            tanks[key] = tank
            
    except* (AttributeError, TypeError):
        _log.error(f'Data parsing error, \n{traceback.format_exc()}')
        raise data_parser.DataParserError()
    else:
        return data
    
def get_session_stats(data_old: PlayerGlobalData, data_new: PlayerGlobalData, zero_bypass: bool = False) -> SessionDiffData:
    '''
    Return stats difference
    '''
    try:
        diff_battles = data_new.data.statistics.all.battles - data_old.data.statistics.all.battles
        tank_stats = _generate_tank_session_dict(data_old, data_new)
        battles_not_updated = True if diff_battles == 0 else False
        r_diff_battles = data_new.data.statistics.rating.battles - data_old.data.statistics.rating.battles
        rating_not_updated = True if r_diff_battles == 0 else False

        if (battles_not_updated and rating_not_updated) and not zero_bypass:
            _log.debug('Different data generating error: player data not updated')
            raise data_parser.NoDiffData('Different data generating error: player data not updated')
        
        if (battles_not_updated and rating_not_updated) and zero_bypass:
            return SessionDiffData.model_validate(
                {
                    'main_diff': dict(),
                    'main_session' : dict(),
                    'rating_diff' : dict(),
                    'rating_session' : dict(),
                    'tank_stats' : None
                }
            )

        n_data = data_new.data.statistics
        o_data = data_old.data.statistics
        
        hits = n_data.all.hits - o_data.all.hits
        frags = n_data.all.frags - o_data.all.frags
        wins = n_data.all.wins - o_data.all.wins
        losses = n_data.all.losses - o_data.all.losses
        capture_points = n_data.all.capture_points - o_data.all.capture_points
        damage_dealt = n_data.all.damage_dealt - o_data.all.damage_dealt
        damage_received = n_data.all.damage_received - o_data.all.damage_received
        shots = n_data.all.shots - o_data.all.shots
        xp = n_data.all.xp - o_data.all.xp
        survived_battles = n_data.all.survived_battles - o_data.all.survived_battles
        dropped_capture_points = n_data.all.dropped_capture_points - o_data.all.dropped_capture_points
        
        r_hits = n_data.rating.hits - o_data.rating.hits
        r_frags = n_data.rating.frags - o_data.rating.frags
        r_wins = n_data.rating.wins - o_data.rating.wins
        r_losses = n_data.rating.losses - o_data.rating.losses
        r_capture_points = n_data.rating.capture_points - o_data.rating.capture_points
        r_damage_dealt = n_data.rating.damage_dealt - o_data.rating.damage_dealt
        r_damage_received = n_data.rating.damage_received - o_data.rating.damage_received
        r_shots = n_data.rating.shots - o_data.rating.shots
        r_xp = n_data.rating.xp - o_data.rating.xp
        r_survived_battles = n_data.rating.survived_battles - o_data.rating.survived_battles
        r_dropped_capture_points = n_data.rating.dropped_capture_points - o_data.rating.dropped_capture_points
        
        diff_mm_rating = n_data.rating.mm_rating - o_data.rating.mm_rating
        diff_rating = n_data.rating.rating - o_data.rating.rating
        r_diff_avg_damage = n_data.rating.avg_damage - o_data.rating.avg_damage
        r_diff_winrate = n_data.rating.winrate - o_data.rating.winrate
        r_diff_avg_spotted = n_data.rating.avg_spotted - o_data.rating.avg_spotted
        r_diff_accuracy = n_data.rating.accuracy - o_data.rating.accuracy
        r_diff_damage_ratio = n_data.rating.damage_ratio - o_data.rating.damage_ratio
        r_diff_destruction_ratio = n_data.rating.destruction_ratio - o_data.rating.destruction_ratio
        r_diff_frags_per_battle = n_data.rating.frags_per_battle - o_data.rating.frags_per_battle
        r_diff_survival_ratio = n_data.rating.survival_ratio - o_data.rating.survival_ratio
        r_diff_avg_spotted = n_data.rating.avg_spotted - o_data.rating.avg_spotted
        
        diff_winrate = n_data.all.winrate - o_data.all.winrate
        diff_avg_damage = n_data.all.avg_damage - o_data.all.avg_damage
        diff_accuracy = n_data.all.accuracy - o_data.all.accuracy
        diff_damage_ratio = n_data.all.damage_ratio - o_data.all.damage_ratio
        diff_destruction_ratio = n_data.all.destruction_ratio - o_data.all.destruction_ratio
        diff_frags_per_battle = n_data.all.frags_per_battle - o_data.all.frags_per_battle
        diff_survival_ratio = n_data.all.survival_ratio - o_data.all.survival_ratio
        diff_avg_spotted = n_data.all.avg_spotted - o_data.all.avg_spotted

       
        session_winrate = safe_divide(wins, diff_battles, 0) * 100
        session_avg_damage = int(safe_divide(damage_dealt, diff_battles, 0))
        session_accuracy = safe_divide(hits, shots, 0) * 100
        session_damage_ratio = safe_divide(damage_dealt, damage_received, 0)
        session_destruction_ratio = safe_divide(frags, (diff_battles - survived_battles), 0)
        session_frags_per_battle = safe_divide(frags, diff_battles, 0)
        session_survival_ratio = safe_divide(wins, diff_battles, 0)
        session_avg_spotted = safe_divide(n_data.all.spotted, diff_battles, 0)

        session_rating = diff_mm_rating * 100 + 3000
        r_session_winrate = safe_divide(r_wins, r_diff_battles) * 100
        r_session_avg_damage = int(safe_divide(r_damage_dealt, r_diff_battles))
        r_session_accuracy = safe_divide(r_hits, r_shots) * 100
        r_session_damage_ratio = safe_divide(r_damage_dealt, r_damage_received)
        r_session_destruction_ratio = safe_divide(r_frags, (r_diff_battles - r_survived_battles))
        r_session_frags_per_battle = safe_divide(r_frags, r_diff_battles)
        r_session_survival_ratio = safe_divide(r_wins, r_diff_battles)
        r_session_avg_spotted = safe_divide(n_data.rating.spotted, r_diff_battles)
            

        diff_data_dict = {
            'main_diff' : {
                'hits': hits,
                'frags': frags,
                'wins': wins,
                'losses': losses,
                'capture_points': capture_points,
                'battles': diff_battles,
                'damage_dealt': damage_dealt,
                'damage_received': damage_received,
                'shots': shots,
                'xp': xp,
                'survived_battles': survived_battles,
                'dropped_capture_points': dropped_capture_points,
                
                'winrate': diff_winrate,
                'avg_damage': diff_avg_damage,
                'battles': diff_battles,
                'accuracy': diff_accuracy,
                'damage_ratio': diff_damage_ratio,
                'destruction_ratio': diff_destruction_ratio,
                'frags_per_battle': diff_frags_per_battle,
                'survival_ratio': diff_survival_ratio,
                'avg_spotted': diff_avg_spotted
            },

            'main_session' : {
                'hits' : hits,
                'frags' : frags,
                'wins' : wins,
                'losses' : losses,
                'capture_points' : capture_points,
                'battles' : diff_battles,
                'damage_dealt' : damage_dealt,
                'damage_received' : damage_received,
                'shots' : shots,
                'xp' : xp,
                'survived_battles' : survived_battles,
                'dropped_capture_points' : dropped_capture_points,
                
                'winrate': session_winrate,
                'avg_damage': session_avg_damage,
                'battles': diff_battles,
                'accuracy': session_accuracy,
                'damage_ratio': session_damage_ratio,
                'destruction_ratio': session_destruction_ratio,
                'frags_per_battle': session_frags_per_battle,
                'survival_ratio': session_survival_ratio,
                'avg_spotted': session_avg_spotted
            },

            'rating_diff' : {
                'hits': r_hits,
                'frags': r_frags,
                'wins': r_wins,
                'losses': r_losses,
                'capture_points': r_capture_points,
                'battles': r_diff_battles,
                'damage_dealt': r_damage_dealt,
                'damage_received': r_damage_received,
                'shots': r_shots,
                'xp': r_xp,
                'survived_battles': r_survived_battles,
                'dropped_capture_points': r_dropped_capture_points,
                'rating': diff_rating,
                
                'winrate': r_diff_winrate,
                'avg_damage': r_diff_avg_damage,
                'battles': r_diff_battles,
                'accuracy': r_diff_accuracy,
                'damage_ratio': r_diff_damage_ratio,
                'destruction_ratio': r_diff_destruction_ratio,
                'frags_per_battle': r_diff_frags_per_battle,
                'survival_ratio': r_diff_survival_ratio,
                'avg_spotted': r_diff_avg_spotted
            },

            'rating_session' : {
                'hits' : r_hits,
                'frags' : r_frags,
                'wins' : r_wins,
                'losses' : r_losses,
                'capture_points' : r_capture_points,
                'battles' : r_diff_battles,
                'damage_dealt' : r_damage_dealt,
                'damage_received' : r_damage_received,
                'shots' : r_shots,
                'xp' : r_xp,
                'survived_battles' : r_survived_battles,
                'dropped_capture_points' : dropped_capture_points,
                'rating': session_rating,
                
                'winrate': r_session_winrate,
                'avg_damage': r_session_avg_damage,
                'battles': r_diff_battles,
                'accuracy': r_session_accuracy,
                'damage_ratio': r_session_damage_ratio,
                'destruction_ratio': r_session_destruction_ratio,
                'frags_per_battle': r_session_frags_per_battle,
                'survival_ratio': r_session_survival_ratio,
                'avg_spotted': r_session_avg_spotted
            },
            'tank_stats' : tank_stats,
        }

    except KeyError as e:
        raise data_parser.DataParserError(e)

    else:
        return SessionDiffData.model_validate(diff_data_dict)

def _generate_tank_session_dict(data_old: PlayerGlobalData, data_new: PlayerGlobalData) -> None | dict[str, TankSessionData]:
    if not isinstance(data_old, PlayerGlobalData) or not isinstance(data_new, PlayerGlobalData):
        raise TypeError('Wrong data type, expected PlayerGlobalData for both data_old and data_new')
    
    tank_stats = None
    tanks = data_new.data.tank_stats
    tanks_old = data_old.data.tank_stats

    diff_battles = []

    for _, (key, tank) in enumerate(tanks.items()):
        tank_stats: dict = {}
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
            tank_type = ''
            tank_name = 'Unknown'
            tank_tier = 0
        
        tank_diff_battles = tanks[tank_id].all.battles - tanks_old[tank_id].all.battles
        
        if tank_diff_battles == 0:
            continue
        
        # Common data
        hits = tanks[tank_id].all.hits - tanks_old[tank_id].all.hits
        frags = tanks[tank_id].all.frags - tanks_old[tank_id].all.frags
        wins = tanks[tank_id].all.wins - tanks_old[tank_id].all.wins
        losses = tanks[tank_id].all.losses - tanks_old[tank_id].all.losses
        capture_points = tanks[tank_id].all.capture_points - tanks_old[tank_id].all.capture_points
        damage_dealt = tanks[tank_id].all.damage_dealt - tanks_old[tank_id].all.damage_dealt
        damage_received = tanks[tank_id].all.damage_received - tanks_old[tank_id].all.damage_received
        shots = tanks[tank_id].all.shots - tanks_old[tank_id].all.shots
        xp = tanks[tank_id].all.xp - tanks_old[tank_id].all.xp
        survived_battles = tanks[tank_id].all.survived_battles - tanks_old[tank_id].all.survived_battles
        dropped_capture_points = tanks[tank_id].all.dropped_capture_points - tanks_old[tank_id].all.dropped_capture_points
        spotted = tanks[tank_id].all.spotted - tanks_old[tank_id].all.spotted
        
        # Diff data
        d_winrate = tanks[tank_id].all.winrate - tanks_old[tank_id].all.winrate
        d_avg_damage = tanks[tank_id].all.avg_damage - tanks_old[tank_id].all.avg_damage
        d_accuracy = tanks[tank_id].all.accuracy - tanks_old[tank_id].all.accuracy
        d_damage_ratio = tanks[tank_id].all.damage_ratio - tanks_old[tank_id].all.damage_ratio
        d_destruction_ratio = tanks[tank_id].all.destruction_ratio - tanks_old[tank_id].all.destruction_ratio
        d_frags_per_battle = tanks[tank_id].all.frags_per_battle - tanks_old[tank_id].all.frags_per_battle
        d_avg_spotted = tanks[tank_id].all.avg_spotted - tanks_old[tank_id].all.avg_spotted
        d_survival_ratio = tanks[tank_id].all.survival_ratio - tanks_old[tank_id].all.survival_ratio
        
        # Session data
        s_avg_damage = damage_dealt // tank_diff_battles
        s_winrate = wins / tank_diff_battles * 100
        s_accuracy = safe_divide(hits, shots) * 100
        s_damage_ratio = safe_divide(damage_dealt, damage_received)
        s_destruction_ratio = safe_divide(frags, (tank_diff_battles - survived_battles))
        s_frags_per_battle = frags / tank_diff_battles
        s_avg_spotted = spotted // tank_diff_battles
        s_survival_ratio = survived_battles / tank_diff_battles
        
        tank_stats.setdefault(tank_id, {
                'tank_name': tank_name,
                'tank_tier': tank_tier,
                'tank_type': tank_type,
                'tank_id' : int(tank_id),
                
                'd_hits' : hits,
                'd_frags' : frags,
                'd_wins' : wins,
                'd_losses' : losses,
                'd_capture_points' : capture_points,
                'd_damage_dealt' : damage_dealt,
                'd_damage_received' : damage_received,
                'd_shots' : shots,
                'd_xp' : xp,
                'd_survived_battles' : survived_battles,
                'd_dropped_capture_points' : dropped_capture_points,
            
                'd_winrate': d_winrate,
                'd_avg_damage': d_avg_damage,
                'd_battles': tank_diff_battles,
                'd_accuracy': d_accuracy,
                'd_damage_ratio': d_damage_ratio,
                'd_destruction_ratio': d_destruction_ratio,
                'd_frags_per_battle': d_frags_per_battle,
                'd_avg_spotted': d_avg_spotted,
                'd_survival_ratio' : d_survival_ratio,
                
                's_hits' : hits,
                's_frags' : frags,
                's_wins' : wins,
                's_losses' : losses,
                's_capture_points' : capture_points,
                's_damage_dealt' : damage_dealt,
                's_damage_received' : damage_received,
                's_shots' : shots,
                's_xp' : xp,
                's_survived_battles' : survived_battles,
                's_dropped_capture_points' : dropped_capture_points,
                
                's_winrate': s_winrate,
                's_avg_damage': s_avg_damage,
                's_battles': tank_diff_battles,
                's_accuracy': s_accuracy,
                's_damage_ratio': s_damage_ratio,
                's_destruction_ratio': s_destruction_ratio,
                's_frags_per_battle': s_frags_per_battle,
                's_avg_spotted': s_avg_spotted,
                's_survival_ratio' : s_survival_ratio
        })
    
    return tank_stats