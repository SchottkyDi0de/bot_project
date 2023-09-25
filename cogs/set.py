import traceback

from discord import Option
from discord.ext import commands

from lib.exceptions.database import DatabaseError
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.locale.locale import Text
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.blacklist.blacklist import data
from lib.logger.logger import get_logger
from lib.settings.settings import SttObject

_log = get_logger(__name__, 'CogSetLogger', 'logs/cog_set.log')


class Set(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = PlayersDB()
        self.sdb = ServersDB()
        
    @commands.slash_command(guild_only=True)
    async def set_lang(self, ctx, 
            lang: Option(
                str,
                description=Text().data.cmd_description.lang,
                choices=SttObject().get().default.available_locales,
                required=True
            )
        ):

        if ctx.author.id in data:
            await ctx.respond(embed=ErrorMSG().user_banned)
            return
        
        Text().load(lang)
        
        try:
            self.sdb.set_lang(ctx.guild.id, lang, ctx.guild.name)
            await ctx.respond(embed=InfoMSG().set_lang_ok)
        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error)
        
    @commands.slash_command(guild_only=True)
    async def set_player(self, ctx, 
            nickname: Option(
                str,
                description=Text().data.cmd_description.nickname,
                max_length=24,
                min_length=3,
                required=True
            ),
            region: Option(
                str,
                description=Text().data.cmd_description.region,
                choices=Text().data.common.regions,
                required=True
            )
        ):

        if ctx.author.id in data:
            await ctx.respond(embed=ErrorMSG().user_banned)
            return
        try:
            
            await ctx.defer()
            Text().load(self.sdb.safe_get_lang(ctx.guild.id))

            self.db.set_member(ctx.author.id, nickname, region)
            await ctx.respond(embed=InfoMSG().set_player_ok)
        except Exception :
            _log.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error)
        

    
def setup(bot):
    bot.add_cog(Set(bot))