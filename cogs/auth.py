import traceback

from discord.ext import commands
from lib.logger.logger import get_logger

_log = get_logger(__file__, 'AuthCogLogger', 'logs/auth_cog_logs.log')

class Auth(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(embed=self.inf_msg.cooldown_not_expired())
        # elif isinstance(error, UserBanned):
        #     await ctx.respond(embed=self.err_msg.user_banned())
        else:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())


def setup(bot):
    bot.add_cog(Auth(bot))