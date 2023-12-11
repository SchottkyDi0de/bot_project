import os
from asyncio import sleep
from multiprocessing import Process

import uvicorn
from discord import Intents, Activity, ActivityType
from discord.ext import commands

from lib.api import async_wotb_api
from lib.database import tankopedia
from lib.logger.logger import get_logger
from api_server import Server
from lib.exceptions.api import APIError
from lib.settings.settings import Config, EnvConfig
from workers.pdb_checker import PDBWorker

_log = get_logger(__name__, 'MainLogger', 'logs/main.log')

_config = Config().get()

class App():
    def __init__(self):
        self.intents = Intents.default()
        self.pbd_worker = PDBWorker()
        self.intents.message_content = True
        self.bot = commands.Bot(intents=self.intents, command_prefix=_config.default.prefix)
        self.bot.remove_command('help')

        self.extension_names = [
            f"cogs.{filename[:-3]}" for filename in os.listdir("./cogs") if filename.endswith(".py")
            ]

    def load_extension(self, extension_names: list[str]):
        for i in extension_names:
            self.bot.load_extension(i)

    def reload_extension(self, extension_names: list):
        for i in extension_names:
            self.bot.reload_extension(i)

    async def apply_presence(self):
        await self.bot.change_presence(
            activity=Activity(
                name=f'Servers: {len(self.bot.guilds)}',
                type=ActivityType.watching
            )
        )
        _log.debug('Presence applied')

    def main(self):

        @self.bot.event
        async def on_ready():
            _log.info('Bot started: %s', self.bot.user)

            tp = tankopedia.TanksDB()
            api = async_wotb_api.API()

            tp.set_tankopedia(await self.retrieve_tankopedia(api))
            _log.debug('Tankopedia set successfull\nBot started: %s', self.bot.user)
            await self.pbd_worker.run_worker()

            await sleep(5)
            await self.apply_presence()

        self.load_extension(self.extension_names)
        self.bot.run(EnvConfig.DISCORD_TOKEN_DEV)

    @staticmethod 
    async def retrieve_tankopedia(api: async_wotb_api.API) -> dict:
        tankopedia_server_list = ['ru', 'eu']
        for i in tankopedia_server_list:
            try:
                return await api.get_tankopedia(i)
            except APIError:
                _log.warning('Failed to get tankopedia data, trying next server...')

        if not Config().settings.internal.ignore_tankopedia_failures:
            _log.critical('Failed to get tankopedia data')
            quit(1)
        
        _log.info('Failed to get tankopedia data, ignoring...')

if __name__ == '__main__':
    app = App()
    app.main()
