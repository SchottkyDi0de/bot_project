from os import system
from os.path import exists
from datetime import datetime
from threading import Thread

from discord import File
from discord.ext.commands import Bot

from lib.dump_handler.zip import Zip, Buffer
from lib.settings.settings import Config
from lib.logger.logger import get_logger

_config = Config().get()
_log = get_logger(__file__, 'DumpHandlerLogger', 'logs/dump_handler.log')


class BackUp:
    def __init__(self):
        self.files: list[Buffer]

    async def _export_archive(self, bot: Bot):
        send_to_id = _config.dump.export_to_id

        member = await bot.fetch_user(send_to_id)
        channel = bot.get_channel(send_to_id)
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if member or channel:
            if len(self.files) > 1:
                files = []
                for buffer in self.files:
                    files += [File(buffer.buffer, f"dump.zip_part{buffer.file_num}")]
            else:
                files = [File(self.files[0].buffer, "dump.zip")]
        if member:
            await member.send(f'Dump created {time}', files=files)
        elif channel:
            await channel.send(f"Dump {time}", files=files)
    
    async def dump(self, bot: Bot):
        _log.info("Worker: Creating dump")
        system(r"lib\dump_handler\bin\mongodump.exe")

        if not exists("dump"):
            _log.error('Failed to create dump')
            return
        
        thread = Thread(target=Zip().get_archive, args=(self,))
        thread.start()

        while thread.is_alive():
            ...
        
        _log.info('Dump created. Exporting...')
        await self._export_archive(bot)
        
    