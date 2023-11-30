import os
from asyncio import sleep

import uvicorn
from discord import Intents, Activity, ActivityType
from discord.ext import commands

import server
from lib.api import async_wotb_api
from lib.database import tankopedia
from lib.logger import logger
from lib.settings.settings import Config
from workers.pdb_checker import PDBWorker

_log = logger.get_logger(__name__, 'MainLogger', 'logs/main.log')

st = Config().get()


class App():
    def __init__(self):
        self.intents = Intents.default()
        self.pbd_worker = PDBWorker()
        self.intents.message_content = True
        self.bot = commands.Bot(intents=self.intents, command_prefix=st.default.prefix)
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
        self.bot.run(st.DISCORD_TOKEN_DEV)
        # uvicorn.run(server.app, host='blitzhub.ru')

    # DEPRECATED, NEED REFACTOR >>>>>>>>
    @staticmethod 
    async def retrieve_tankopedia(api: async_wotb_api.API, n_retries: int = 2) -> dict:
        for _ in range(n_retries):
            try:
                return await api.get_tankopedia('ru')
            except Exception:
                _log.error('', exc_info=True)
        quit(1)
    # DEPRECATED, NEED REFACTOR <<<<<<<<


if __name__ == '__main__':
    app = App()
    app.main()
