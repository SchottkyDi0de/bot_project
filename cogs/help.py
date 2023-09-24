import traceback

from discord import Option
from discord.ext import commands

from lib.locale.locale import Text
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.logger.logger import get_logger

_logger = get_logger(__name__, 'CogHelpLogger', 'logs/cog_help.log')


class Help(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(guild_only=True, description=Text().get().cmd_description.help)
    async def help(
        self, 
        ctx,
        h_type: Option(
            str,
            description=Text().data.cmd_description.help_types,
            choices=Text().data.help.types,
            required=True
            )
        ):
        try:
            try:
                match h_type:
                    case 'syntax':
                        await ctx.user.send(embed=InfoMSG().help_syntax)
                    case 'setup':
                        await ctx.user.send(embed=InfoMSG().help_setup)
                    case 'statistics':
                        await ctx.user.send(embed=InfoMSG().help_statistics)
                    case 'session':
                        await ctx.user.send(embed=InfoMSG().help_session)
                    case _:
                        await ctx.respond(embed=ErrorMSG().unknown_error)
            except:
                match h_type:
                    case 'syntax':
                        await ctx.respond(embed=InfoMSG().help_syntax)
                    case 'setup':
                        await ctx.respond(embed=InfoMSG().help_setup)
                    case 'statistics':
                        await ctx.respond(embed=InfoMSG().help_statistics)
                    case 'session':
                        await ctx.respond(embed=InfoMSG().help_session)
                    case _:
                        await ctx.respond(embed=ErrorMSG().unknown_error)
        except:
            _logger.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error)


def setup(bot):
    bot.add_cog(Help(bot))