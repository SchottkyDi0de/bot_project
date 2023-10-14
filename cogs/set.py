import traceback

from discord import Option
from discord.ext import commands

from lib.settings.settings import SttObject
from lib.exceptions.database import MemberNotFound
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.locale.locale import Text
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.blacklist.blacklist import check_user
from lib.exceptions.blacklist import UserBanned
from lib.logger.logger import get_logger
from lib.settings.settings import SttObject

_log = get_logger(__name__, 'CogSetLogger', 'logs/cog_set.log')


class Set(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = PlayersDB()
        self.sdb = ServersDB()
        self.err_msg = ErrorMSG()
        self.inf_msg = InfoMSG()
        
    @commands.slash_command(guild_only=True)
    async def set_lang(self, ctx: commands.Context,
            lang: Option(
                str,
                description=Text().get().cmds.set_lang.descr.sub_descr.lang_list,
                choices=SttObject().get().default.available_locales,
                required=True
            ),
            to_server: Option(
                bool,
                description=Text().get().cmds.set_lang.descr.sub_descr.to_server,
                default=False
            )
        ):

        try:
            check_user(ctx)
        except UserBanned:
            return
        
        Text().load_from_context(ctx)
        
        if to_server:
            if not ctx.author.guild_permissions.administrator:
                await ctx.respond(embed=self.err_msg.set_lang_perm())
                return
            try:
                self.sdb.set_lang(ctx.guild.id, lang, ctx.guild.name)
                Text().load(self.sdb.safe_get_lang(ctx.guild.id))
                await ctx.respond(embed=self.inf_msg.set_lang_ok())
            except Exception:
                _log.error(traceback.format_exc())
                await ctx.respond(embed=self.err_msg.unknown_error())
        else:
            try:
                self.db.set_member_lang(ctx.author.id, lang)
                Text().load_from_context(ctx)
            except MemberNotFound:
                await ctx.respond(embed=self.err_msg.set_lang_unregistred())
            else:
                await ctx.respond(embed=self.inf_msg.set_lang_ok())
        
    @commands.slash_command(guild_only=True)
    async def set_player(self, ctx: commands.Context, 
            nickname: Option(
                str,
                description=Text().get().frequent.common.nickname,
                max_length=24,
                min_length=3,
                required=True
            ),
            region: Option(
                str,
                description=Text().get().frequent.common.region,
                choices=SttObject().get().default.available_regions,
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