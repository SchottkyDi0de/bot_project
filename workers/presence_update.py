from asyncio import sleep

from discord import Status, Bot, Activity, ActivityType

from lib.logger.logger import get_logger

_log = get_logger(__file__, 'UpdatePresenceWorker', 'logs/update_prescence_worker.log')


class PresenceUpdater:
    def __init__(self):
        self.STOP_FLAG = False
        
    async def run_worker(self, bot: Bot):
        _log.info('WORKERS: Presence worker started')
        while not self.STOP_FLAG:
            await bot.change_presence(
                activity=Activity(
                    name=f'Servers: {len(bot.guilds)}',
                    type=ActivityType.watching,
                ),
                status=Status.online
            )
            _log.debug('Presence updated')
            await sleep(1200)
            
        _log.info('WORKERS: Prescence worker stopped')
            