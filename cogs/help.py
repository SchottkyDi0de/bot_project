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
        self.err_msg = ErrorMSG()
        self.inf_msg = InfoMSG()

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
        Text().load_from_context(ctx)
        check_user(ctx)

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
                case 'ua':
                    await ctx.author.send(
                        embed=InfoMSG().custom(
                            Text().get(),
                            title=Text().get().cmds.help.items.help,
                            text=_config.help_urls.ua
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
                case 'ua':
                    await ctx.respond(
                        embed=InfoMSG().custom(
                            Text().get(),
                            title=Text().get().cmds.help.items.help,
                            text=_config.help_urls.ua
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
            
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(embed=self.inf_msg.cooldown_not_expired())
        elif isinstance(error, UserBanned):
            await ctx.respond(embed=self.err_msg.user_banned())
        else:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())


def setup(bot):
    bot.add_cog(Help(bot))