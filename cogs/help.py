import traceback
from asyncio import sleep

from discord import Option
from discord.ext import commands

from lib.database.servers import ServersDB
from lib.locale.locale import Text
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.logger.logger import get_logger

_logger = get_logger(__name__, 'CogHelpLogger', 'logs/cog_help.log')


class Help(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.sdb = ServersDB()

    @commands.slash_command(guild_only=True, description=Text().get().cmd_description.help)
    async def help(
        self, 
        ctx,
        h_type: Option(
            str,
            description=Text().get().cmd_description.help_types,
            choices=Text().get().help.types,
            required=True
            )
        ):
        try:
            Text().load(self.sdb.safe_get_lang(ctx.guild.id))
            try:
                match h_type:
                    case 'syntax':
                        await ctx.user.send(embed=InfoMSG().help_syntax)
                        ctx.respond(embed=InfoMSG().help_send_ok)
                    case 'setup':
                        await ctx.user.send(embed=InfoMSG().help_setup)
                        ctx.respond(embed=InfoMSG().help_send_ok)
                    case 'statistics':
                        await ctx.user.send(embed=InfoMSG().help_statistics)
                        ctx.respond(embed=InfoMSG().help_send_ok)
                    case 'session':
                        await ctx.user.send(embed=InfoMSG().help_session)
                        ctx.respond(embed=InfoMSG().help_send_ok)
                    case 'all':
                        for i in Text().get().help.types:
                            if i == 'all':
                                continue
                            await ctx.user.send(embed=getattr(InfoMSG(), f'help_{i}'))
                            await sleep(0.5)
                        await ctx.respond(embed=InfoMSG().help_send_ok)
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
                    case 'all':
                        for i in Text().get().help.types:
                            if i == 'all':
                                await ctx.respond(embed=InfoMSG().help_send_ok)
                            await ctx.user.send(embed=getattr(InfoMSG(), f'help_{i}'))
                            await sleep(0.5)
                    case _:
                        await ctx.respond(embed=ErrorMSG().unknown_error)
        except:
            _logger.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error)


def setup(bot):
    bot.add_cog(Help(bot))