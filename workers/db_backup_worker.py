from asyncio import sleep
from datetime import datetime
from typing import TYPE_CHECKING

from pytz import timezone

from lib.logger.logger import get_logger

from lib.dump_handler import BackUp

if TYPE_CHECKING:
    from aiogram import Bot

_log = get_logger(__file__, 'TgDBBackupWorkerLogger', 'logs/db_backup_worker.log')


class DBBackupWorker:
    def __init__(self):
        self.STOP_FLAG = True   #TODO: set to False

    def stop_worker(self):
        _log.debug('WORKERS: setting STOP_WORKER_FLAG to True')
        self.STOP_FLAG = True
    
    async def run_worker(self, bot: 'Bot', *args):
        _log.info('WORKERS: DB backup worker started')
        while not self.STOP_FLAG:
            if datetime.now(timezone('Europe/Moscow')).hour == 12:
                await BackUp().dump(bot)
            await sleep(1800)
