import traceback

from discord import File
from discord.ext import commands

from lib.api.async_wotb_api import API
from lib.data_classes.api_data import PlayerGlobalData
from lib.data_parser.parse_data import get_session_stats
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.exceptions import api, data_parser, database
from lib.image.session import ImageGen
from lib.locale.locale import Text
from lib.blacklist.blacklist import data
from lib.logger.logger import get_logger
from lib.data_classes.api_data import PlayerGlobalData
from datetime import datetime

_log = get_logger(__name__, 'CogSessionLogger', 'logs/cog_session.log')


class Session(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = PlayersDB()
        self.sdb = ServersDB()
        self.api = API()
        
    @commands.slash_command(guild_only=True, description=Text().data.cmd_description.start_session)
    async def start_session(self, ctx):
        if ctx.author.id in data:
            await ctx.respond(embed=ErrorMSG().user_banned)
            return
        
        await ctx.defer()
        try:
            Text().load(self.sdb.safe_get_lang(ctx.guild.id))

            if self.db.check_member(ctx.author.id):
                member = self.db.get_member(ctx.author.id)
                try:
                    data = await self.api.get_stats(member['nickname'], member['region'], raw_dict=False)
                    self.db.set_member_last_stats(ctx.author.id, data.to_dict())
                except database.LastStatsNotFound:
                    await ctx.respond(embed=ErrorMSG().session_not_found)
                    return
                
                await ctx.respond(embed=InfoMSG().session_started)
                return

            await ctx.respond(embed=InfoMSG().player_not_registred_session)
        except Exception as e:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error)

    @commands.slash_command(guild_only=True, description=Text().get().cmd_description.get_session)
    async def get_session(self, ctx):
        if ctx.author.id in data:
            await ctx.respond(embed=ErrorMSG().user_banned)
            return
        
        await ctx.defer()
        try:
            Text().load(self.sdb.safe_get_lang(ctx.guild.id))

            if self.db.check_member(ctx.author.id):
                member = self.db.get_member(ctx.author.id)

                try:
                    stats = await self.api.get_stats(member['nickname'], member['region'])
                except api.APIError:
                    ctx.respond(embed=ErrorMSG().api_error)
                    return
                
                try:
                    last_stats = PlayerGlobalData(self.db.get_member_last_stats(member['id']))
                except database.LastStatsNotFound:
                    await ctx.respond(embed=ErrorMSG().session_not_found)
                    return

                try:
                    diff_stats = get_session_stats(last_stats, stats)
                except data_parser.NoDiffData:
                    await ctx.respond(embed=ErrorMSG().session_not_updated)
                    return

                image = ImageGen().generate(stats, diff_stats)
                await ctx.respond(file=File(image, 'session.png'))
                return
            
            await ctx.respond(embed=InfoMSG().player_not_registred_session)
        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error)

    @commands.slash_command(guild_only=True, description='None')
    async def session_state(self, ctx):
        if ctx.author.id in data:
            await ctx.respond(embed=ErrorMSG().user_banned)
            return
        
        try:
            member_registred = self.db.check_member(ctx.author.id)
            if member_registred:
                session_started = self.db.check_member_last_stats(ctx.author.id)
                if session_started:
                    try:
                        last_stats = self.db.get_member_last_stats(ctx.author.id)
                    except database.LastStatsNotFound():
                        _log.error(traceback.format_exc())
                        await ctx.respond(embed=ErrorMSG().session_not_found)
                        return
                    
                    session_timestamp = last_stats['timestamp']
                    time_format = f'%H{Text().get().time_units.hours} : %M{Text().get().time_units.minuts}'
                    session_age = datetime.utcfromtimestamp(datetime.now().timestamp() - session_timestamp).strftime(time_format)

                    text = f'{Text().get().session_state.started}\n{Text().get().session_state.age}{session_age}'
                    await ctx.respond(f'```{text}```')
                else:
                    await ctx.respond(f'```{Text().get().session_state.not_started}```')
            else:
                await ctx.respond(f'```{Text().get().session_state.player_not_registred}```')

        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error)

    
def setup(bot):
    bot.add_cog(Session(bot))