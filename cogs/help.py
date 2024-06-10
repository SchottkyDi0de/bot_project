from discord import errors
from discord.ext import commands
from discord.commands import ApplicationContext

from lib.blacklist.blacklist import check_user
from lib.database.servers import ServersDB
from lib.database.players import PlayersDB
from lib.locale.locale import Text
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.error_handler.common import hook_exceptions
from lib.logger.logger import get_logger
from lib.settings.settings import Config

_log = get_logger(__file__, 'CogHelpLogger', 'logs/cog_help.log')
_config = Config().get()


class Help(commands.Cog):
    cog_command_error = hook_exceptions(_log)
    
    def __init__(self, bot) -> None:
        self.bot = bot
        self.sdb = ServersDB()
        self.pdb = PlayersDB()
        self.err_msg = ErrorMSG()
        self.inf_msg = InfoMSG()

    @commands.slash_command(
            guild_only=True,
            name=Text().get('en').cmds.help.items.help.lower(),
            name_localizations={
                'ru': Text().get('ru').cmds.help.items.help.lower(),
                'pl': Text().get('pl').cmds.help.items.help.lower(),
                'uk': Text().get('ua').cmds.help.items.help.lower()
            },
            description=Text().get('en').cmds.help.descr.this,
            description_localizations={
                'ru': Text().get('ru').cmds.help.descr.this,
                'pl': Text().get('pl').cmds.help.descr.this,
                'uk': Text().get('ua').cmds.help.descr.this
                },
            )
    async def help(
        self, 
        ctx: ApplicationContext,
        ):
        await Text().load_from_context(ctx)
        check_user(ctx)

        await ctx.defer()
        try:
            match Text().current_lang:
                case 'ru':
                    await ctx.author.send(
                        embed=InfoMSG().custom(
                            Text().get('ru'),
                            title=Text().get('ru').cmds.help.items.help,
                            text=_config.help_urls.ru
                            )
                        )
                case 'ua':
                    await ctx.author.send(
                        embed=InfoMSG().custom(
                            Text().get('ua'),
                            title=Text().get('ua').cmds.help.items.help,
                            text=_config.help_urls.ua
                        )
                    )
                case 'pl':
                    await ctx.author.send(
                        embed=InfoMSG().custom(
                            Text().get('pl'),
                            title=Text().get('pl').cmds.help.items.help,
                            text=_config.help_urls.pl
                            )
                        )
                case _:
                    await ctx.author.send(
                        embed=InfoMSG().custom(
                            Text().get('en'),
                            title=Text().get('en').cmds.help.items.help,
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
                            Text().get('ru'),
                            title=Text().get('ru').cmds.help.items.help,
                            text=_config.help_urls.ru
                            )
                        )
                case 'ua':
                    await ctx.respond(
                        embed=InfoMSG().custom(
                            Text().get('ua'),
                            title=Text().get('ua').cmds.help.items.help,
                            text=_config.help_urls.ua
                        )
                    )
                case 'pl':
                    await ctx.respond(
                        embed=InfoMSG().custom(
                            Text().get('pl'),
                            title=Text().get('pl').cmds.help.items.help,
                            text=_config.help_urls.pl
                        )
                    )
                case _:
                    await ctx.respond(
                        embed=InfoMSG().custom(
                            Text().get('en'),
                            title=Text().get('en').cmds.help.items.help,
                            text=_config.help_urls.en
                            )
                        )
            await ctx.respond(embed=InfoMSG().help_send_ok())


def setup(bot):
    bot.add_cog(Help(bot))