from asyncio import sleep

from lib.logger.logger import get_logger

from lib.cooldown.cooldown import CooldownStorage

_log = get_logger(__file__, 'TgCStorageCleanerWorkerLogger', 'logs/cstorage_cleaner_worker.log')


class CooldownStorageCleanerWorker:
    def __init__(self):
        self.STOP_FLAG = False
    
    def stop_worker(self):
        """
        Stop the worker.

        This function sets the STOP_WORKER_FLAG to True, indicating that the worker should stop processing tasks.

        Parameters:
            None

        Returns:
            None
        """
        _log.debug('WORKERS: setting STOP_WORKER_FLAG to True')
        self.STOP_FLAG = True
    
    async def run_worker(self, *_):
        while not self.STOP_FLAG:
            for group_name in CooldownStorage.storage:
                CooldownStorage.storage[group_name].clear_storage()
            await sleep(300)
