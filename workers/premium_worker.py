from asyncio import sleep
from datetime import datetime, timedelta
from discord import Bot
import pytz

from lib.database.players import PlayersDB
from lib.logger.logger import get_logger
from lib.settings.settings import Config
from lib.database.internal import InternalDB

_log = get_logger(__file__, 'PremiumWorkerLogger', 'logs/premium_worker.log')
_config = Config().get()


class UpdatePremiumWorker:
    def __init__(self) -> None:
        self.STOP_FLAG = False
        
    async def _update_players(self, bot: Bot):
        premium_members = await InternalDB().get_actual_premium_users()
        for member_id in await PlayersDB().get_all_members_ids():
            if member_id in premium_members:
                await PlayersDB().set_premium(member_id, datetime.now(pytz.utc) + timedelta(days=1))
                _log.info(f"Set premium for {member_id}")
            else:
                await PlayersDB().check_premium(member_id, None)

    async def run_worker(self, bot: Bot):
        _log.info('WORKERS: Premium worker started')
        while not self.STOP_FLAG:
            await self._update_players(bot)
            await sleep(240)
            
    def stop_worker(self):
        _log.info('WORKERS: Premium worker stopped')
        self.STOP_FLAG = True
