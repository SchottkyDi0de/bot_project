import asyncio
import json
from time import time
from datetime import datetime

import aiohttp

if __name__ == '__main__':
    import os
    import sys
    # Тебе нужно уметь запускать этот скрипт самостоятельно, верно?
    # Если да, то этот трюк не совсем нужен, должно сработать вот так из корня проекта:
    # python -m lib.api.async_wotb_api
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

_log = get_logger(__name__, 'AsyncWotbAPILogger', 'logs/async_wotb_api.log')
st = settings.SttObject()


# Я бы не писал кэш вручную, а использовал что-то готовое вроде
# https://pypi.org/project/cachetools/
class APICache:
    cache: dict = {}
    cache_ttl: int = 60  # seconds
    cache_size: int = 40  # items

    def check_item(self, key):
        return key in self.cache.keys()

    def _overflow_handler(self):
        overflow = len(self.cache.keys()) - self.cache_size
        if overflow > 0:
            keys = list(self.cache.keys())[:overflow]
            for key in keys:
                self.cache.pop(key)

    def del_item(self, key):
        del self.cache[key]

    def check_timestamp(self, key):
        current_time = datetime.now().timestamp()
        timestamp = self.cache[key].timestamp
        time_delta = current_time - timestamp
        return time_delta <= self.cache_ttl

    def add_item(self, item: PlayerGlobalData):
        self._overflow_handler()
        self.cache[(item.lower_nickname, item.region)] = item

    def get_item(self, key):
        if self.check_item(key):
            if self.check_timestamp(key):
                return self.cache[key]

        raise KeyError('Cache miss')


class API:
    def __init__(self) -> None:
        self.account_id = 0
        self.cache = APICache()
        self.player = PlayerGlobalData()
        self.exact = True
        self.nickname = ''
        self.region = ''
        self.need_cached = False
        self.raw_dict = False

        self.start_time = 0

    def _get_id_by_reg(self, reg: str):
        reg = reg.lower()
        if reg == 'ru':
            return st.LT_APP_ID
        elif reg in ['eu', 'com', 'asia', 'na', 'as']:
            return st.WG_APP_ID
        raise api_exceptions.UncorrectRegion(f'Uncorrect region: {reg}')

    def _reg_normalizer(self, reg: str) -> str:
        if reg in ['ru', 'eu', 'asia']:
            return reg
        if reg == 'na':
            return 'com'
        else:
            raise api_exceptions.UncorrectRegion(f'Uncorrect region: {reg}')

    def _get_url_by_reg(self, reg: str):
        reg = self._reg_normalizer(reg)
        match reg:
            case 'ru':
                return 'papi.tanksblitz.ru'
            case 'eu':
                return 'api.wotblitz.eu'
            case 'asia':
                return 'api.wotblitz.asia'
            case 'com':
                return 'api.wotblitz.com'
            case _:
                raise api_exceptions.UncorrectRegion(f'Uncorrect region: {reg}')

    async def get_tankopedia(self, region: str = 'ru') -> dict:

        _log.debug('Get tankopedia data')
        url_get_tankopedia = (
            f'https://{self._get_url_by_reg(region)}/wotb/encyclopedia/vehicles/'
            f'?application_id={self._get_id_by_reg(region)}&fields='
            f'-description%2C+-engines%2C+-guns%2C-next_tanks%2C+-prices_xp%2C+'
            f'-suspensions%2C+-turrets%2C+-cost%2C+-default_profile%2C+-modules_tree%2C+-images'
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url_get_tankopedia) as response:
                # Здесь можно было бы вызывать `response.raise_for_status()` вместо ручной проверки, но не критично
                if response.status != 200:
                    raise api_exceptions.APIError()

                data = await response.json()

                if data['status'] == 'error':
                    _log.error(f'Error get tankopedia, bad response status: \n{data}')
                    raise api_exceptions.APIError(f'Bad API response status {data}')

                return data

    async def get_stats(self, search: str, region: str, exact: bool = True, raw_dict: bool = False) -> PlayerGlobalData:
        if search is None or region is None:
            self.exact = True
            self.raw_dict = False
            self.nickname = ''
            self.region = ''
            self.account_id = 0
            raise api_exceptions.APIError('Empty parameter search or region')

        # Здесь может быть проблема: получается, что вызов `get_stats()` переключает `API`
        # потенциально на другой регион. Если не аккуратно запрограммировать, то можно
        # наткнуться на интересные баги, например, что будет использован неправильный регион.
        # Лучше было бы не сохранять их в аттрибутах вообще, а всегда принимать через параметры.
        self.exact = exact
        self.raw_dict = raw_dict
        self.nickname = search
        self.region = region

        _log.debug('Get stats method called, arguments: %s, %s', search, region)
        self.start_time = time()
        self.need_cached = False
        try:
            cached_data = self.cache.get_item((search.lower(), region))
        except KeyError:
            self.need_cached = True
            _log.debug('Cache miss')
        else:
            _log.debug('Returned cached player data')
            return cached_data
        

        tasks = [
            self.get_player_stats,
            self.get_player_tanks_stats,
            self.get_player_clan_stats,
            self.get_player_achievements
        ]

        await self.get_account_id()
        async with aiohttp.ClientSession() as self.session:
            async with asyncio.TaskGroup() as tg:
                for task in tasks:
                    task = tg.create_task(task())
                    await task
                    # Мне не очень понятно, зачем используется `TaskGroup`, ведь
                    # `await task` автоматически делает этот код последовательным
                    # (ждем одну таску, потом следующую и так далее).
                    # Здесь можно было бы использовать `asyncio.gather()`,
                    # если хотелось их запрашивать параллельно.

        _log.debug(f'All requests time: {time() - self.start_time}')
        return get_normalized_data(self.player)

    async def get_account_id(self):
        url_get_id = (
            f'https://{self._get_url_by_reg(self.region)}/wotb/account/list/'
            f'?application_id={self._get_id_by_reg(self.region)}'
            f'&search={self.nickname}'
            f'&type={"exact" if self.exact else "startswith"}'
        )

        async with aiohttp.ClientSession() as self.session:
            async with self.session.get(url_get_id) as response:
                # Проверки статуса и результата повторяются для каждого метода API.
                # Можно было бы вынести эту общую логику в отдельный метод.
                if response.status != 200:
                    raise api_exceptions.APIError()

                data = await response.text()
                data = json.loads(data)

                if data['status'] == 'error':
                    match data['error']['code']:
                        case 407 | 402:
                            raise api_exceptions.UncorrectName()
                if data['meta']['count'] > 1:
                    raise api_exceptions.MoreThanOnePlayerFound()
                elif data['meta']['count'] == 0:
                    raise api_exceptions.NoPlayersFound()

                self.account_id: int = data['data'][0]['account_id']
                data = None

    async def get_player_stats(self):

        url_get_stats = (
            f'https://{self._get_url_by_reg(self.region)}/wotb/account/info/'
            f'?application_id={self._get_id_by_reg(self.region)}'
            f'&account_id={self.account_id}'
            f'&extra=statistics.rating'
            f'&fields=-statistics.clan'
        )

        async with self.session.get(url_get_stats) as response:
            if response.status != 200:
                raise api_exceptions.APIError(f'Bad response code {response.status}')

            data = await response.json()  # ниже такие же штуки

            if data['status'] != 'ok':
                raise api_exceptions.APIError(f'Bad API response status {data}')

            data['data'] = data['data'][str(self.account_id)]
            data = PlayerStats(data)

            try:
                battles = data.data.statistics.all.battles
            except (KeyError, AttributeError):
                raise api_exceptions.EmptyDataError('Cannot acces to field "battles" in the output data')
            else:
                if battles < 100:
                    raise api_exceptions.NeedMoreBattlesError('Need more battles for generate statistics')
                else:
                    self.player.id = self.account_id
                    self.player.data = data.data
                    self.player.nickname = data.data.nickname

            data = None

    async def get_player_achievements(self):
        url_get_achievements = (
            f'https://{self._get_url_by_reg(self.region)}/wotb/account/achievements/'
            f'?application_id={self._get_id_by_reg(self.region)}'
            f'&fields=-max_series&account_id={self.account_id}'
        )

        async with self.session.get(url_get_achievements) as response:
            if response.status != 200:
                raise api_exceptions.APIError(f'Bad response code {response.status}')

            data = await response.text()
            data = json.loads(data)

            if data['status'] != 'ok':
                raise api_exceptions.APIError(f'Bad API response status {data}')

            self.player.data.achievements = Achievements(data['data'][str(self.account_id)]['achievements'])

            data = None

    async def get_player_clan_stats(self):
        url_get_clan_stats = (
            f'https://{self._get_url_by_reg(self.region)}/wotb/clans/accountinfo/'
            f'?application_id={self._get_id_by_reg(self.region)}'
            f'&account_id={self.account_id}'
            f'&extra=clan'
        )

        try:
            async with self.session.get(url_get_clan_stats) as response:
                if response.status != 200:
                    raise api_exceptions.APIError(f'Bad response code {response.status}')

                clan_tag = None

                data = await response.text()
                data = json.loads(data)

                if data['status'] != 'ok':
                    raise api_exceptions.APIError(f'Bad API response status {data}')

                try:
                    clan_tag = data['data'][str(self.account_id)]['clan']['tag']
                except AttributeError as e:
                    raise api_exceptions.APIError(e)
                else:
                    data['data'] = data['data'][str(self.account_id)]
                    data = ClanStats(data)
                    self.player.data.clan_tag = clan_tag
                    self.player.data.clan_stats = data.data.clan

        # Ловить Exception, чаще всего, плохая идея: как минимум, будет трудно отлаживать.
        # Лучше ловить конкретные типы исключений.
        except Exception:
            self.player.data.clan_tag = 'NONE'
            self.player.data.clan_stats = None

    async def get_player_tanks_stats(self):
        url_get_tanks_stats = (
            f'https://{self._get_url_by_reg(self.region)}/wotb/tanks/stats/'
            f'?application_id={self._get_id_by_reg(self.region)}'
            f'&account_id={self.account_id}'
        )
        async with self.session.get(url_get_tanks_stats) as response:

            if response.status != 200:
                raise api_exceptions.APIError(f'Bad response code {response.status}')

            data = await response.text()
            data = json.loads(data)

            if data['status'] != 'ok':
                raise api_exceptions.APIError(f'Bad API response status \n{data}')

            tanks_stats: list[TankStats] = []

            for i in data['data'][str(self.account_id)]:
                tanks_stats.append(TankStats(i))

            self.player.timestamp = datetime.now().timestamp()

            self.player.region = self._reg_normalizer(self.region)
            self.player.lower_nickname = self.nickname.lower()
            self.player.data.tank_stats = tanks_stats

            if self.need_cached:
                self.cache.add_item(self.player)
                _log.debug('Data add to cache')

            # _log.debug('%s', return_data)
            if self.raw_dict:
                return self.player.to_dict()


def test(nickname='cnJIuHTeP_KPbIca', region='ru', save_to_database: bool = False):
    db = PlayersDB()
    api = API()
    data = asyncio.run(api.get_stats(nickname, region), debug=True)
    
    if save_to_database:
        db.set_member_last_stats(766019191836639273, data.to_dict())

    return data
