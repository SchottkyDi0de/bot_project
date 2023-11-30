import os
import traceback

from discord.ext import commands
from asyncio import sleep
from discord import Bot
from lib.logger.logger import get_logger
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from datetime import datetime
from lib.blacklist import blacklist

_admin_ids = [
    766019191836639273
]

_log = get_logger(__name__, 'AdminCogLogger', 'logs/admin.log')


class AdminCommand(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.sdb = ServersDB()
        self.pdb = PlayersDB()
        self.extension_names = []

        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                self.extension_names.append(f"cogs.{filename[:-3]}")


    @commands.slash_command()
    async def test(self, ctx: commands.Context):
        await ctx.respond('Ты не должен был это видеть...')
        _log.debug('Yay!')

def setup(bot):
    bot.add_cog(AdminCommand(bot))