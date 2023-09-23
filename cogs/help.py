import traceback

from discord import Option
from discord.ext import commands

from lib.locale.locale import Text
from lib.embeds.errors import ErrorMSG
from lib.logger.logger import get_logger

_logger = get_logger(__name__, 'CogHelpLogger', 'logs/cog_help.log')


class Help():
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(guild_only=True, description=Text().get().cmd_description.help)
    async def help(
        self, 
        ctx,
        h_type: Option(
            str,
            description=Text().data.cmd_description.help_types,
            choices=Text().data.common.help.types,
            required=True
            )
        ):
        try:
            try:
                await ctx.member.send(embed=getattr(Text().get(), h_type))
            except:
                await ctx.respond(embed=getattr(Text().get(), h_type))
        except:
            _logger.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error)


def setup(bot):
    bot.add_cog(Help())