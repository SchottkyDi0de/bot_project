import os

from discord import Intents
from discord.ext import commands

from lib.api import async_wotb_api
from lib.database import tankopedia
from lib.logger import logger
from lib.settings import settings

_log = logger.get_logger(__name__, 'MainLogger', 'logs/main.log')

st = settings.SttInit().get()


class App():
    def __init__(self):
        self.intents = Intents.default()
        self.bot = commands.Bot(intents=self.intents, command_prefix='!')
        self.bot.remove_command('help')
        
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                self.bot.load_extension(f"cogs.{filename[:-3]}")
        
    def main(self):
        @self.bot.event
        async def on_ready():
            _log.info('Bot started: %s', self.bot.user)
            tp = tankopedia.TanksDB()
            api = async_wotb_api.API()
            tanks_data = await api.get_tankopedia()
            tp.set_tankopedia(tanks_data)
            _log.debug('Tankopedia set successfull')

        self.bot.run(st.DISCORD_TOKEN)


if __name__ == '__main__':
    app = App()
    app.main()
