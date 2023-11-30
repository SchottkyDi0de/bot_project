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

_log = get_logger(__name__, 'CogHelpLogger', 'logs/cog_help.log')


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
        h_type: Option(
            str,
            description=Text().get().cmds.help.descr.sub_descr.help_types,
            description_localizations={
                'ru': Text().get('ru').cmds.help.descr.sub_descr.help_types,
                'pl': Text().get('pl').cmds.help.descr.sub_descr.help_types,
                'uk': Text().get('ua').cmds.help.descr.sub_descr.help_types
                },
            choices=Text().get().cmds.help.items.help_types,
            default='all'
            )
        ):
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        try:
            Text().load_from_context(ctx)
            await ctx.defer()
            try:
                match h_type:
                    case 'syntax':
                        await ctx.user.send(embed=InfoMSG().help_syntax())
                    case 'setup':
                        await ctx.user.send(embed=InfoMSG().help_setup())
                    case 'statistics':
                        await ctx.user.send(embed=InfoMSG().help_statistics())
                    case 'session':
                        await ctx.user.send(embed=InfoMSG().help_session())
                    case 'other':
                        await ctx.user.send(embed=InfoMSG().help_other())
                    case 'all':
                        for i in Text().get().cmds.help.items.help_types:
                            if i == 'all':
                                continue
                            await ctx.user.send(embed=getattr(InfoMSG(), f'help_{i}')())
                            await sleep(0.5)
                    case _:
                        await ctx.respond(embed=ErrorMSG().unknown_error())
                await ctx.respond(embed=InfoMSG().help_send_ok())
                return
            except errors.Forbidden:
                try:
                    match h_type:
                        case 'syntax':
                            await ctx.channel.send(embed=InfoMSG().help_syntax())
                        case 'setup':
                            await ctx.channel.send(embed=InfoMSG().help_setup())
                        case 'statistics':
                            await ctx.channel.send(embed=InfoMSG().help_statistics())
                        case 'session':
                            await ctx.channel.send(embed=InfoMSG().help_session())
                        case 'other':
                            await ctx.channel.send(embed=InfoMSG().help_other())
                        case 'all':
                            for i in Text().get('en').cmds.help.items.help_types:
                                if i == 'all':
                                    continue
                                await ctx.channel.send(embed=getattr(InfoMSG(), f'help_{i}')())
                                await sleep(0.5)
                        case _:
                            await ctx.respond(embed=ErrorMSG().unknown_error())
                            return
                except Exception:
                    await ctx.respond(embed=ErrorMSG().unknown_error())
                    _log.error(traceback.format_exc())
                    return
                await ctx.respond(embed=InfoMSG().help_send_ok())
        except:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error())


def setup(bot):
    bot.add_cog(Help(bot))