from asyncio import sleep

from lib.database.utils.dump_handler import BackUp
from lib.logger.logger import get_logger

_log = get_logger(__file__, 'DBBackupWorkerLogger', 'logs/db_backup_worker.log')


class DBBackupWorker:
    def __init__(self):
        self.STOP_FLAG = False
    
    async def run_worker(self, *args):
        _log.info('WORKERS: DB backup worker started')
        while not self.STOP_FLAG:
            BackUp().dump()
            await sleep(3600 * 24)
