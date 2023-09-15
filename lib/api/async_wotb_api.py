import asyncio
import json
from datetime import datetime

import aiohttp

if __name__ == '__main__':
    import os
    import sys
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    sys.path.insert(0, path)

from lib.data_classes.api_data import PlayerGlobalData
from lib.data_classes.palyer_clan_stats import ClanStats
from lib.data_classes.player_achievements import Achievements
from lib.data_classes.player_stats import PlayerStats
from lib.data_classes.tanks_stats import TankStats
from lib.data_parser.parse_data import get_normalized_data
from lib.database.players import PlayersDB
from lib.exceptions import api as api_exceptions
from lib.logger.logger import get_logger
from lib.settings import settings
from lib.yaml.yaml2object import Parser

_log = get_logger(__name__, 'AsyncWotbAPILogger', 'logs/async_wotb_api.log')
st = settings.SttObject()


class APICache():
    cache: dict = {}
    cache_ttl: int = 60 # seconds
    cache_size: int = 40 # items
    
    def check_item(self, key):
        if key in self.cache.keys():
            return True
        return False
        
    def _overflow_handler(self):
        overflow = len(self.cache.keys()) - self.cache_size
        if overflow > 0:
            for i in range(overflow):
                key = list(self.cache.keys())[i]
                self.cache.pop(key)
                
    def del_item(self, key):
        del self.cache[key]
        
    def check_timestamp(self, key):
        current_time = datetime.now().timestamp()
        timestamp = self.cache[key].timestamp
        time_delta = current_time - timestamp
        if time_delta > self.cache_ttl:
            return False
        else:
            return True
        
    def add_item(self, item: PlayerGlobalData):
        self._overflow_handler()
        self.cache[(item.lower_nickname, item.region)] = item
        
    def get_item(self, key):
        if self.check_item(key):
            if self.check_timestamp(key):
                return self.cache[key]
        
        raise KeyError('Cache miss')


class API():
    def __init__(self) -> None:
        self.account_id = 0
        self.cache = APICache()
    
    def _get_id_by_reg(self, reg: str):
        reg = reg.lower()
        if reg == 'ru':
            return st.LT_APP_ID
        elif reg in ['eu', 'com', 'asia']:
            return st.WG_APP_ID
        
    def _reg_normalizer(self, reg: str) -> str:
        if reg in ['ru', 'eu', 'asia']:
            return reg
        if reg in ['na', 'as']:
            match reg:
                case 'na':
                    return 'com'
                case 'as':
                    return 'asia'
                case _:
                    raise api_exceptions.UncorrectRegion(f'Uncorrect region: {reg}')

    async def get_tankopedia(self, region: str = 'ru') -> dict:

        _log.debug('Get tankopedia data')
        url_get_tankopedia = (
            f'https://api.wotblitz.{region}/wotb/encyclopedia/vehicles/\
            ?application_id={self._get_id_by_reg(region)}&fields=\
            -description%2C+-engines%2C+-guns%2C-next_tanks%2C+-prices_xp%2C+\
            -suspensions%2C+-turrets%2C+-cost%2C+-default_profile%2C+-modules_tree%2C+-images').strip()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url_get_tankopedia) as response:
                if response.status != 200:
                    raise api_exceptions.APIError()
                
                data = await response.text()
                data = json.loads(data)

                if data['status'] == 'error':
                    _log.error(f'Error get tankopedia, bad response status: \n{data}')
                    raise api_exceptions.APIError(f'Bad API response status {data}')
                        
                await session.close()
                return data
        
    async def get_stats(self, search: str, region: str, exact: bool = True, raw_dict: bool = False) -> PlayerGlobalData:
        if search is None or region is None:
            raise api_exceptions.APIError('Empty parameter search or region')
        
        _log.debug('Get stats method called, arguments: %s, %s', search, region)
        need_cached = False
        try:
            cached_data = self.cache.get_item((search.lower(), region))
        except KeyError:
            need_cached = True
            _log.debug('Cache miss')
        else:
            _log.debug('Returned cached player data')
            return cached_data
        
        self.account_id = 0
        url_get_id = (
            f'https://api.wotblitz.{self._reg_normalizer(region)}/wotb/account/list/\
            ?application_id={self._get_id_by_reg(region)}\
            &search={search}\
            &type={"exact" if exact else "startswith"}').strip()

        async with aiohttp.ClientSession() as session:
            async with session.get(url_get_id) as response:
                if response.status != 200:
                    raise api_exceptions.APIError()
                
                data = await response.text()
                data = json.loads(data)

                if data['status'] == 'error':
                    match data.error.code:
                        case 407 | 402:
                            raise api_exceptions.UncorrectName()
                if data['meta']['count'] > 1:
                    raise api_exceptions.MoreThanOnePlayerFound()
                elif data['meta']['count'] == 0:
                    raise api_exceptions.NoPlayersFound()
                
                account_id: int = data['data'][0]['account_id']
                data = None
                
                url_get_stats = (
                    f'https://api.wotblitz.{self._reg_normalizer(region)}/wotb/account/info/\
                    ?application_id={self._get_id_by_reg(region)}\
                    &account_id={account_id}\
                    &extra=statistics.rating\
                    &fields=-statistics.clan').strip()
                
                async with session.get(url_get_stats) as response:
                    if response.status != 200:
                        raise api_exceptions.APIError(f'Bad response code {response.status}')

                    data = await response.text()
                    data = json.loads(data)

                    if data['status'] != 'ok':
                        raise api_exceptions.APIError(f'Bad API response status {data}')
                    
                    data['data'] = data['data'][str(account_id)]
                    data = PlayerStats(data)

                    try:
                        battles = data.data.statistics.all.battles
                    except (KeyError, AttributeError):
                        raise api_exceptions.EmptyDataError('Cannot acces to field "battles" in the output data')
                    else:
                        if battles < 100:
                            raise api_exceptions.NeedMoreBattlesError('Need more battles for generate statistics')
                        else:
                            player = PlayerGlobalData()
                            player.id = account_id
                            player.data = data.data
                            player.nickname = data.data.nickname
                    
                    data = None
                
                url_get_achievements = (
                    f'https://api.wotblitz.{self._reg_normalizer(region)}/wotb/account/achievements/\
                    ?application_id={self._get_id_by_reg(region)}\
                    &fields=-max_series&account_id={account_id}').strip()
                
                async with session.get(url_get_achievements) as response:
                    if response.status != 200:
                        raise api_exceptions.APIError(f'Bad response code {response.status}')

                    data = await response.text()
                    data = json.loads(data)

                    if data['status'] != 'ok':
                        raise api_exceptions.APIError(f'Bad API response status {data}')
                    
                    player.data.achievements = Achievements(data['data'][str(account_id)]['achievements'])

                    data = None
                    
                url_get_clan_stats = (
                    f'https://api.wotblitz.{self._reg_normalizer(region)}/wotb/clans/accountinfo/\
                    ?application_id={self._get_id_by_reg(region)}\
                    &account_id={account_id}\
                    &extra=clan').strip()
                
                async with session.get(url_get_clan_stats) as response:
                    if response.status != 200:
                        raise api_exceptions.APIError(f'Bad response code {response.status}')
                    
                    clan_tag = None

                    data = await response.text()
                    data = json.loads(data)

                    if data['status'] != 'ok':
                        raise api_exceptions.APIError(f'Bad API response status {data}')
                    
                    try:
                        clan_tag = data['data'][str(account_id)]['clan']['tag']
                    except AttributeError as e:
                        raise api_exceptions.APIError(e) 
                    else:
                        data['data'] = data['data'][str(account_id)]
                        data = ClanStats(data)
                        player.data.clan_tag = clan_tag
                        player.data.clan_stats = data.data.clan

                url_get_tanks_stats = \
                        f'https://api.wotblitz.{self._reg_normalizer(region)}/wotb/tanks/stats/\
                        ?application_id={self._get_id_by_reg(region)}\
                        &account_id={player.id}'
                        
                async with session.get(url_get_tanks_stats) as response:
                    if response.status != 200:
                        raise api_exceptions.APIError(f'Bad response code {response.status}')
                    
                    data = await response.text()
                    data = json.loads(data)

                    if data['status'] != 'ok':
                        raise api_exceptions.APIError(f'Bad API response status {data}')
                    
                    tanks_stats: list[TankStats] = []

                    for i in data['data'][str(player.id)]:
                        tanks_stats.append(TankStats(i))

                    player.timestamp = datetime.now().timestamp()
                    
                    player.region = self._reg_normalizer(region)
                    player.lower_nickname = player.data.nickname.lower()
                    player.data.tank_stats = tanks_stats
                    
                    if need_cached:
                        self.cache.add_item(player)
                        _log.debug('Data add to cache')
                        
                    # _log.debug('%s', return_data)
                    if raw_dict:
                        return player.to_dict()

                    return get_normalized_data(player)


def test(nickname = 'cnJIuHTeP_KPbIca', region = 'ru', save_to_database: bool = False):
    db = PlayersDB()
    api = API()
    data = asyncio.run(api.get_stats(nickname, region))

    if save_to_database:
        db.set_member_last_stats(766019191836639273, get_normalized_data(data).to_dict())

    return get_normalized_data(data)
