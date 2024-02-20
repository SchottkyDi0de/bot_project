from discord.ext import commands
from lib.logger.logger import get_logger
from lib.exceptions.error_handler.error_handler import error_handler

_log = get_logger(__file__, 'AuthCogLogger', 'logs/auth_cog_logs.log')

class Auth(commands.Cog):
    cog_command_error = error_handler(_log)
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


def setup(bot):
    bot.add_cog(Auth(bot))