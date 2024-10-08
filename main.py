"""
Copyright 2024 vladislawzero@gmail.com | _zener_diode | https://github.com/SchottkyDi0de

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), 
  to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
  and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, 
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
  
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

This license applies to all files in this project that contain Python source code unless otherwise specified!
"""
import os
import sys
from asyncio import TaskGroup

from aiohttp import ClientError
from discord import Intents, Activity, Status, ActivityType
from discord.ext import commands

from lib.api import async_wotb_api
from lib.database.tankopedia import TankopediaDB
from lib.logger.logger import get_logger
from lib.exceptions.api import APIError
from lib.settings.settings import Config
from workers.pdb_checker import PDBWorker
from workers.db_backup_worker import DBBackupWorker

_log = get_logger(__file__, 'MainLogger', 'logs/main.log')
_config = Config().get()

try:
    sys.argv[1]
except IndexError:
    print(
        'No token provided!\n'
        'Usage: python main.py <token>\n'
        '=================================\n'
        'RECOMMENDED STARTUP:\n'
        '>>> python launch.py prod (or dev)\n'
    )
    quit(1)

class App():
    def __init__(self):
        self.api = async_wotb_api.API()
        self.backup = DBBackupWorker()
        self.workers_running = False
        self.intents = Intents.default()
        self.pbd_worker = PDBWorker()
        self.bot = commands.Bot(intents=self.intents, command_prefix=_config.default.prefix)
        self.bot.remove_command('help')
        self.workers = [
                self.pbd_worker.run_worker,
                self.backup.run_worker,
            ]

        self.extension_names = [
            f"cogs.{filename[:-3]}" for filename in os.listdir("./cogs") if filename.endswith(".py")
            ]

    def load_extension(self, extension_names: list[str]):
        for i in extension_names:
            self.bot.load_extension(i)

    def reload_extension(self, extension_names: list):
        for i in extension_names:
            self.bot.reload_extension(i)
            
    async def run_workers(self):
        if self.workers_running:
            return
        
        self.workers_running = True
        async with TaskGroup() as tg:
            for worker in self.workers:
                tg.create_task(worker(self.bot))

    def main(self):

        @self.bot.event
        async def on_ready():
            _log.info('Bot started: %s', self.bot.user)

            await self.retrieve_tankopedia(self.api)
            _log.debug('Tankopedia set successful\nBot started: %s', self.bot.user)
            
            await self.bot.change_presence(
                activity=Activity(
                    name=f'Servers: {len(self.bot.guilds)}',
                    type=ActivityType.watching,
                ),
                status=Status.online
            )
            await self.run_workers()
        
        self.load_extension(self.extension_names)
        self.bot.run(sys.argv[1])

    @staticmethod
    async def retrieve_tankopedia(api: async_wotb_api.API) -> dict:
        tankopedia_server_list = ['eu', 'ru']
        fail_counter = 0
        for region in tankopedia_server_list:
            try:
                data = await api.get_tankopedia(region=region)
            except (APIError, ClientError, TimeoutError):
                _log.error(f'Failed to get tankopedia data in {region}, trying next server...')
                fail_counter += 1
            else:
                await TankopediaDB().set_tanks(tanks=data, region=region)
                _log.info(f'Successfully got tankopedia data in {region}')
                
        if fail_counter == len(tankopedia_server_list) and not _config.internal.ignore_tankopedia_failures:
            _log.fatal('Failed to get tankopedia data in all servers')
            quit(1)


if __name__ == '__main__':
    app = App()
    app.main()
