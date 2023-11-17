import traceback

from discord import Option
from discord.ext import commands

from lib.settings.settings import Config
from lib.exceptions.database import MemberNotFound
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.locale.locale import Text
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.blacklist.blacklist import check_user
from lib.exceptions.blacklist import UserBanned
from lib.logger.logger import get_logger
from lib.settings.settings import Config

_log = get_logger(__name__, 'CogSetLogger', 'logs/cog_set.log')


class Set(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = PlayersDB()
        self.sdb = ServersDB()
        self.err_msg = ErrorMSG()
        self.inf_msg = InfoMSG()
        
    @commands.slash_command(
            guild_only=True,
            description=Text().get().cmds.set_lang.descr.this,
            description_localizations={
                'ru': Text().get('ru').cmds.set_lang.descr.this,
                'pl': Text().get('pl').cmds.set_lang.descr.this,
                'uk': Text().get('ua').cmds.set_lang.descr.this
                }
            )
    async def set_lang(self, ctx: commands.Context,
            lang: Option(
                str,
                description=Text().get().cmds.set_lang.descr.sub_descr.lang_list,
                description_localizations={
                    'ru': Text().get('ru').cmds.set_lang.descr.sub_descr.lang_list,
                    'pl': Text().get('pl').cmds.set_lang.descr.sub_descr.lang_list,
                    'uk': Text().get('ua').cmds.set_lang.descr.sub_descr.lang_list
                },
                choices=Config().get().default.available_locales,
                required=True
            ),
        ):


        try:
            check_user(ctx)
        except UserBanned:
            return
        
        try:
            Text().load_from_context(ctx)
            lang = None if lang == 'auto' else lang
            if self.db.set_member_lang(ctx.author.id, lang):
                Text().load_from_context(ctx)
            else:
                await ctx.respond(embed=self.err_msg.set_lang_unregistred())
                return
            
            await ctx.respond(embed=self.inf_msg.set_lang_ok())
        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())
        
    @commands.slash_command(guild_only=True)
    async def set_player(self, ctx: commands.Context, 
            nickname: Option(
                str,
                description=Text().get().frequent.common.nickname,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.nickname,
                    'pl': Text().get('pl').frequent.common.nickname,
                    'uk': Text().get('ua').frequent.common.nickname
                },
                max_length=24,
                min_length=3,
                required=True
            ),
            region: Option(
                str,
                description=Text().get().frequent.common.region,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.region,
                    'pl': Text().get('pl').frequent.common.region,
                    'uk': Text().get('ua').frequent.common.region
                },
                choices=Config().get().default.available_regions,
                required=True
            )
        ):

        try:
            check_user(ctx)
        except UserBanned:
            return
        
        try:
            await ctx.defer()
            Text().load_from_context(ctx)

            self.db.set_member(ctx.author.id, nickname, region)
            await ctx.respond(embed=self.inf_msg.set_player_ok())
        except Exception :
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())
        

def setup(bot):
    bot.add_cog(Set(bot))