import traceback

from discord.ext import commands


class Auth(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


def setup(bot):
    bot.add_cog(Auth(bot))