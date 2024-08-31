from asyncio import sleep
from datetime import datetime

import pytz

from discord.ext.commands import Bot

from lib.dump_handler.dump_handler import BackUp
from lib.logger.logger import get_logger

_log = get_logger(__file__, 'DBBackupWorkerLogger', 'logs/db_backup_worker.log')


class DBBackupWorker:
    def __init__(self):
        self.STOP_FLAG = False

    def stop_worker(self):
        _log.debug('WORKERS: setting STOP_WORKER_FLAG to True')
        self.STOP_FLAG = True
    
    async def run_worker(self, bot: Bot, *args):
        _log.info('WORKERS: DB backup worker started')
        while not self.STOP_FLAG:
            if datetime.now(pytz.utc).hour == 4:
                await BackUp().dump(bot)
            await sleep(1800)
