from datetime import time, datetime, timedelta
import traceback

from discord import File
from discord.ext import commands

from lib.api.async_wotb_api import API
from lib.blacklist.blacklist import check_user
from lib.data_classes.api_data import PlayerGlobalData
from lib.data_parser.parse_data import get_session_stats
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.exceptions import api, data_parser, database
from lib.exceptions.blacklist import UserBanned
from lib.image.session import ImageGen
from lib.data_classes.api_data import PlayerGlobalData
from lib.utils.string_parser import insert_data
from lib.locale.locale import Text
from lib.logger.logger import get_logger
from lib.utils.time_converter import TimeConverter
from lib.exceptions.api import APIError

_log = get_logger(__name__, 'CogSessionLogger', 'logs/cog_session.log')


class Session(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = PlayersDB()
        self.sdb = ServersDB()
        self.api = API()
        self.err_msg = ErrorMSG()
        self.inf_msg = InfoMSG()
        
    @commands.slash_command(
            guild_only=True, 
            description=Text().data.cmds.start_session.descr.this
            )
    async def start_session(self, ctx: commands.Context):
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        await ctx.defer()
        try:
            Text().load_from_context(ctx)

            if self.db.check_member(ctx.author.id):
                member = self.db.get_member(ctx.author.id)
                try:
                    last_stats = await self.api.get_stats(member['nickname'], member['region'], raw_dict=False)
                    self.db.set_member_last_stats(ctx.author.id, last_stats.to_dict())
                except database.LastStatsNotFound:
                    await ctx.respond(
                        embed=self.inf_msg.custom(
                            Text().get().cmds.start_session.info.player_not_registred
                        )
                    )
                    return
                
                await ctx.respond(embed=self.inf_msg.session_started())
                return

            await ctx.respond(embed=self.inf_msg.player_not_registred_session())
        except Exception as e:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())

    @commands.slash_command(
            guild_only=True, 
            description=Text().get().cmds.get_session.descr.this)
    async def get_session(self, ctx):
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        await ctx.defer()
        try:
            Text().load_from_context(ctx)

            if self.db.check_member(ctx.author.id):
                member = self.db.get_member(ctx.author.id)

                try:
                    stats = await self.api.get_stats(member['nickname'], member['region'])
                except api.APIError:
                    await ctx.respond(embed=self.err_msg.api_error())
                    return
                
                try:
                    last_stats = PlayerGlobalData(self.db.get_member_last_stats(member['id']))
                except database.LastStatsNotFound:
                    await ctx.respond(embed=self.err_msg.session_not_found())
                    return

                try:
                    diff_stats = get_session_stats(last_stats, stats)
                except data_parser.NoDiffData:
                    await ctx.respond(embed=self.err_msg.session_not_updated())
                    return

                image = ImageGen().generate(stats, diff_stats)
                await ctx.respond(file=File(image, 'session.png'))
                return
            
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get().cmds.get_session.info.player_not_registred,
                    'orange'
                    )
                )
        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())

    @commands.slash_command(guild_only=True, description='None')
    async def session_state(self, ctx: commands.Context):
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        try:
            Text().load_from_context(ctx)
            member_registred = self.db.check_member(ctx.author.id)
            if member_registred:
                session_started = self.db.check_member_last_stats(ctx.author.id)
                if session_started:
                    try:
                        last_stats = PlayerGlobalData(self.db.get_member_last_stats(ctx.author.id))
                    except database.LastStatsNotFound:
                        await ctx.respond(embed=self.err_msg.session_not_found())
                        return
                    
                    session_timestamp = last_stats.timestamp
                    time_format = f'%H{Text().get().frequent.common.time_units.h} : %M{Text().get().frequent.common.time_units.m}'
                    passed_time = datetime.now().timestamp() - session_timestamp
                    time_left = 86400 - passed_time
                    try:
                        battles_before = last_stats.data.statistics.all.battles
                        battles_after = await self.api.get_player_battles(last_stats.region, str(last_stats.id))
                    except APIError:
                        _log.error(traceback.format_exc())
                        await ctx.respond(embed=self.err_msg.api_error())
                        return
                    except (AttributeError, TypeError):
                        _log.error(traceback.format_exc())
                        await ctx.respond(embed=self.err_msg.unknown_error())
                        return

                    text = insert_data(
                        Text().get().cmds.session_state.items.started,
                        ('time', 'time_left', 'battles'),
                        (
                            TimeConverter.formatted_from_secs(int(passed_time), time_format),
                            TimeConverter.formatted_from_secs(int(time_left), time_format),
                            str(battles_after - battles_before)
                        )
                    )
                    
                    await ctx.respond(embed=self.inf_msg.session_state(text))
                else:
                    await ctx.respond(
                        embed=self.inf_msg.custom(
                            Text().get().cmds.session_state.items.not_started,
                            'orange'
                            )
                        )
            else:
                await ctx.respond(
                    embed=self.inf_msg.custom(
                        Text().get().cmds.session_state.info.player_not_registred,
                        'orange'
                        )
                    )

        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())

    
def setup(bot):
    bot.add_cog(Session(bot))