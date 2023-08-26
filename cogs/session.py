from discord import File, Embed
from discord.ext import commands

from lib.exceptions import database, data_parser
from lib.database import discorddb
from lib.locale.locale import Text
from lib.api.async_wotb_api import API
from lib.embeds import errors, info
from lib.image.session import ImageGen
from lib.data_parser.parse_data import get_session_stats
from lib.data_classes.api_data import PlayerGlobalData
from lib.embeds.info import InfoMSG
from lib.embeds.errors import ErrorMSG
from lib.exceptions import api

class Session(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = discorddb.ServerDB()
        self.inf_msg = info.InfoMSG()
        self.err_msg = errors.ErrorMSG()
        self.api = API()
        
    @commands.slash_command(guild_only=True)
    async def start_session(self, ctx):
        await ctx.defer()
        if self.db.check_member(ctx.author.id):
            member = self.db.get_member(ctx.author.id)
            try:
                data = await self.api.get_stats(member['nickname'], member['region'], raw_dict=False)
                self.db.set_member_last_stats(ctx.author.id, data.to_dict())
            except database.LastStatsNotFound:
                await ctx.respond(embed=ErrorMSG.session_not_found)
                return
            
            await ctx.respond(embed=InfoMSG.session_started)
            return

        await ctx.respond(embed=InfoMSG.player_not_registred_session)

    @commands.slash_command(guild_only=True)
    async def get_session(self, ctx):
        await ctx.defer()
        if self.db.check_member(ctx.author.id):
            member = self.db.get_member(ctx.author.id)

            try:
                stats = await self.api.get_stats(member['nickname'], member['region'])
            except api.APIError:
                ctx.respond(embed=ErrorMSG.api_error)
            
            try:
                last_stats = PlayerGlobalData(self.db.get_member_last_stats(member['id']))
            except database.LastStatsNotFound:
                await ctx.respond(embed=ErrorMSG.session_not_found)
                return

            try:
                diff_stats = get_session_stats(last_stats, stats)
            except data_parser.NoDiffData:
                await ctx.respond(embed=ErrorMSG.session_not_updated)
                return

            image = ImageGen().generate(stats, diff_stats)
            await ctx.respond(file=File(image, 'session.png'))
            return
        
        await ctx.respond(embed=InfoMSG.player_not_registred_session)

    
def setup(bot):
    bot.add_cog(Session(bot))