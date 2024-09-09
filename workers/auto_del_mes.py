from time import time
from asyncio import sleep
from typing import TYPE_CHECKING

from aiohttp import ClientSession

from lib.logger.logger import get_logger
from lib.settings.settings import EnvConfig

if TYPE_CHECKING:
    from aiogram.types import Message

_log = get_logger(__file__, 'TgAutoDelMesWorkerLogger', 'logs/tg_auto_del_mes.log')


class AutoDeleteMessage:
    del_list: list[tuple['Message', int, int]] = []
    url = f"https://api.telegram.org/bot{EnvConfig.TG_TOKEN}/"

    def __init__(self):
        self.STOP_FLAG = False
    
    async def _del_message(self, msg: 'Message'):
        async with self.session as session:
            await session.post(self.url + "deleteMessage", data={
                "chat_id": msg.chat.id,
                "message_id": msg.message_id
            })

    def stop_worker(self):
        _log.debug('WORKERS: setting STOP_WORKER_FLAG to True')
        self.STOP_FLAG = True

    @classmethod
    def add2list(cls, msg: 'Message', del_after: int) -> None:
        cls.del_list.append((msg, del_after, time()))
    
    async def run_worker(self, *_):
        _log.info('WORKERS: AutoDeleteMessage worker started')
        self.session = ClientSession()
        while not self.STOP_FLAG:
            for msg, del_after, start_time in self.del_list:
                if time() - start_time > del_after:
                    await self._del_message(msg)
                    self.del_list.remove((msg, del_after, start_time))
                await sleep(0.1)
            await sleep(3)
