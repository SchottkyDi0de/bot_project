from asyncio import sleep

from discord import Status, Bot, Activity, ActivityType

from lib.logger.logger import get_logger

_log = get_logger(__name__, 'UpdatePresenceWorker', 'logs/update_prescence_worker.log')


class PresenceUpdater:
    def __init__(self):
        self.STOP_FLAG = False
        
    async def run_worker(self, bot: Bot):
        while not self.STOP_FLAG:
            _log.info('WORKERS: Presence worker started')
            await bot.change_presence(
                activity=Activity(
                    name=f'Servers: {len(bot.guilds)}',
                    type=ActivityType.watching,
                ),
                status=Status.streaming
            )
            _log.debug('Presence updated')
            await sleep(300)
            
        _log.info('WORKERS: Prescence worker stopped')
            