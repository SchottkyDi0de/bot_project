import traceback
import os
from pathlib import Path

from discord import Intents
from discord.ext import commands

from lib.api import async_wotb_api
from lib.database import tankopedia
from lib.logger import logger
from lib.settings.settings import SttObject

_log = logger.get_logger(__name__, 'MainLogger', 'logs/main.log')

st = SttObject().get()


class App():
    def __init__(self):
        self.intents = Intents.default()
        self.intents.message_content = True
        self.bot = commands.Bot(intents=self.intents, command_prefix=st.default.prefix)
        self.bot.remove_command('help')

        self.extension_names = [f"cogs.{filename[:-3]}" for filename in os.listdir("./cogs") if filename.endswith(".py")]

    def load_extension(self, extension_names: list[str]):
        for i in extension_names:
            self.bot.load_extension(i)

    def reload_extension(self, extension_names: list):
        for i in extension_names:
            self.bot.reload_extension(i)

    def main(self):

        @self.bot.event
        async def on_ready():
            _log.info('Bot started: %s', self.bot.user)
            tp = tankopedia.TanksDB()
            api = async_wotb_api.API()
            tp.set_tankopedia(await self.retrieve_tankopedia(api))
            _log.debug('Tankopedia set successfull\nBot started: %s', self.bot.user)

        self.load_extension(self.extension_names)
        self.bot.run(st.DISCORD_TOKEN)

    @staticmethod
    async def retrieve_tankopedia(api: async_wotb_api.API, n_retries: int = 2) -> dict:
        for _ in range(n_retries):
            try:
                return await api.get_tankopedia('ru')
            except Exception:
                _log.error('', exc_info=True)
        quit(1)


if __name__ == '__main__':
    app = App()
    app.main()
