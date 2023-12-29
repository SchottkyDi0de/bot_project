import traceback
from asyncio import sleep

from discord import Option, errors
from discord.ext import commands
from lib.blacklist.blacklist import check_user
from lib.exceptions.blacklist import UserBanned
from lib.database.servers import ServersDB
from lib.database.players import PlayersDB
from lib.locale.locale import Text
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.logger.logger import get_logger
from lib.settings.settings import Config

_log = get_logger(__name__, 'CogHelpLogger', 'logs/cog_help.log')
_config = Config().get()


class Help(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.sdb = ServersDB()
        self.pdb = PlayersDB()

    @commands.slash_command(
            guild_only=True,
            name=Text().get().cmds.help.items.help.lower(),
            name_localizations={
                'ru': Text().get('ru').cmds.help.items.help.lower(),
                'pl': Text().get('pl').cmds.help.items.help.lower(),
                'uk': Text().get('ua').cmds.help.items.help.lower()
            },
            description=Text().get().cmds.help.descr.this,
            description_localizations={
                'ru': Text().get('ru').cmds.help.descr.this,
                'pl': Text().get('pl').cmds.help.descr.this,
                'uk': Text().get('ua').cmds.help.descr.this
                },
            )
    async def help(
        self, 
        ctx: commands.Context,
        ):
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        try:
            Text().load_from_context(ctx)
            await ctx.defer()
            try:
                match Text().current_lang:
                    case 'ru':
                        await ctx.author.send(
                            embed=InfoMSG().custom(
                                Text().get(),
                                title=Text().get().cmds.help.items.help,
                                text=_config.help_urls.ru
                                )
                            )
                    case _:
                        await ctx.author.send(
                            embed=InfoMSG().custom(
                                Text().get(),
                                title=Text().get().cmds.help.items.help,
                                text=_config.help_urls.en
                                )
                            )
                        
                await ctx.respond(embed=InfoMSG().help_send_ok())
                return
            
            except errors.Forbidden:
                match Text().current_lang:
                    case 'ru':
                        await ctx.respond(
                            embed=InfoMSG().custom(
                                Text().get(),
                                title=Text().get().cmds.help.items.help,
                                text=_config.help_urls.ru
                                )
                            )
                    case _:
                        await ctx.respond(
                            embed=InfoMSG().custom(
                                Text().get(),
                                title=Text().get().cmds.help.items.help,
                                text=_config.help_urls.en
                                )
                            )
                await ctx.respond(embed=InfoMSG().help_send_ok())
                return

        except:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error())


def setup(bot):
    bot.add_cog(Help(bot))