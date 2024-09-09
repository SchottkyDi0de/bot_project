from typing import TYPE_CHECKING

from os import system, remove
from os.path import exists
from shutil import make_archive
from asyncio import sleep
from datetime import datetime
from threading import Thread

from aiogram.types import BufferedInputFile

from lib.logger.logger import get_logger

from lib.settings import Config

if TYPE_CHECKING:
    from aiogram import Bot

_config = Config().config
_log = get_logger(__file__, 'TgDumpHandlerLogger', 'logs/tg_dump_handler.log')


class BackUp:    
    async def _start_and_wait_for_thread(self, thread: Thread):
        thread.start()
        while thread.is_alive():
            await sleep(0.1)
    
    async def _make_archive(self):
        make_archive('tgdump', 'zip', 'tgdump')
        with open('tgdump.zip', 'rb') as f:
            buffer = BufferedInputFile(f.read(), "backup.zip")

        remove('tgdump.zip')
        return buffer

    async def _export_archive(self, bot: 'Bot'):
        send_to_id = _config.dump_export_to_id
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        await bot.send_document(send_to_id, await self._make_archive(), caption=f'Dump at {time}')
    
    async def dump(self, bot: 'Bot'):
        _log.info("Worker: Creating dump")
        command = r"lib\dump_handler\bin\mongodump.exe --db=TgPlayersDB -o=tgdump"
        await self._start_and_wait_for_thread(Thread(target=lambda: system(command)))

        if not exists("tgdump"):
            _log.error('Failed to create dump')
            return
        
        _log.info('Dump created. Exporting...')
        await self._export_archive(bot)
        
    