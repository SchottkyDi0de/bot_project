import os
import traceback

from discord import Intents
from discord.ext import commands

from lib.api import async_wotb_api
from lib.database import tankopedia
from lib.logger import logger
from lib.settings.settings import SttObject
from lib.embeds.errors import ErrorMSG
from lib.exceptions.blacklist import UserBanned

_log = logger.get_logger(__name__, 'MainLogger', 'logs/main.log')

st = SttObject().get()


class App():
    def __init__(self):
        self.intents = Intents.default()
        self.intents.message_content = True
        self.bot = commands.Bot(intents=self.intents, command_prefix=st.default.prefix)
        self.bot.remove_command('help')
        self.extension_names = []
        
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                self.extension_names.append(f"cogs.{filename[:-3]}")

    def load_extension(self, extension_names: list):
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
            try:
                tanks_data = await api.get_tankopedia()
            except Exception:
                _log.error(traceback.format_exc())
                try:
                    tanks_data = await api.get_tankopedia('eu')
                except Exception:
                    _log.error(traceback.format_exc())
                    _log.error('Get tankopedia failed!')
                    quit(1)
                else:
                    tp.set_tankopedia(tanks_data)
            else:
                tp.set_tankopedia(tanks_data)

            _log.debug('Tankopedia set successfull\nBot started: %s', self.bot.user)

        self.load_extension(self.extension_names)
        self.bot.run(st.DISCORD_TOKEN)


if __name__ == '__main__':
    app = App()
    app.main()
