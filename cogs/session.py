from datetime import time, datetime, timedelta
import traceback

from pydantic import ValidationError

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
    text_obj = Text()

    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = PlayersDB()
        self.sdb = ServersDB()
        self.api = API()
        self.err_msg = ErrorMSG()
        self.inf_msg = InfoMSG()
        
    @commands.slash_command(
            guild_only=True, 
            description=text_obj.datas[text_obj.current_lang].cmds.start_session.descr.this,
            description_localizations={
                'ru': text_obj.get('ru').cmds.start_session.descr.this,
                'pl': text_obj.get('pl').cmds.start_session.descr.this,
                'uk': text_obj.get('ua').cmds.start_session.descr.this
                }
            )
    async def start_session(self, ctx: commands.Context):
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        await ctx.defer()
        try:
            self.text_obj.load_from_context(ctx)

            if self.db.check_member(ctx.author.id):
                member = self.db.get_member(ctx.author.id)
                last_stats = await self.api.get_stats(member.nickname, member.region)
                self.db.set_member_last_stats(ctx.author.id, last_stats.model_dump())
                await ctx.respond(embed=self.inf_msg.session_started())
            else:
                await ctx.respond(
                    embed=self.inf_msg.custom(
                        Text().get(),
                        self.text_obj.get().cmds.start_session.info.player_not_registred
                    )
                )
                return
        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())

    @commands.slash_command(
            guild_only=True, 
            description=text_obj.get().cmds.get_session.descr.this,
            description_localizations={
                'ru': text_obj.get('ru').cmds.get_session.descr.this,
                'pl': text_obj.get('pl').cmds.get_session.descr.this,
                'uk': text_obj.get('ua').cmds.get_session.descr.this
                }
            )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def get_session(self, ctx: commands.Context):
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        await ctx.defer()
        try:
            self.text_obj.load_from_context(ctx)

            if self.db.check_member(ctx.author.id):
                member = self.db.get_member(ctx.author.id)
                image_settings = self.db.get_image_settings(ctx.author.id)
                server_settings = self.sdb.get_server_settings(ctx)

                try:
                    stats = await self.api.get_stats(member.nickname, member.region)
                except api.APIError:
                    await ctx.respond(embed=self.err_msg.api_error())
                    return

                last_stats = self.db.get_member_last_stats(member.id)

                if last_stats is None:
                    await ctx.respond(embed=self.err_msg.session_not_found())
                    return
                
                if isinstance(last_stats['data']['tank_stats'], list):
                    tank_stats_dict = {}
                    for tank in last_stats['data']['tank_stats']:
                        tank_stats_dict[str(tank['tank_id'])] = tank
                    last_stats['data']['tank_stats'] = tank_stats_dict
                
                last_stats = PlayerGlobalData.model_validate(last_stats)

                try:
                    diff_stats = get_session_stats(last_stats, stats)
                except data_parser.NoDiffData:
                    await ctx.respond(embed=self.err_msg.session_not_updated())
                    return
                
                image = ImageGen().generate(stats, diff_stats, ctx, image_settings, server_settings)
                self.db.extend_session(ctx.author.id)
                await ctx.respond(file=File(image, 'session.png'))
                return

            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    self.text_obj.get().cmds.get_session.info.player_not_registred,
                    colour='orange'
                    )
                )

        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())
    
    @get_session.error
    async def on_error(self, ctx: commands.Context, _):
        _log.error(traceback.format_exc())
        await ctx.respond(embed=self.err_msg.cooldown_not_expired())

    @commands.slash_command(
            guild_only=True, 
            description='None',
            description_localizations={
                'ru' : text_obj.get('ru').cmds.session_state.descr.this,
                'pl' : text_obj.get('pl').cmds.session_state.descr.this,
                'uk' : text_obj.get('ua').cmds.session_state.descr.this
                }
            )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def session_state(self, ctx: commands.Context):
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        try:
            self.text_obj.load_from_context(ctx)
            if self.db.check_member(ctx.author.id):
                if self.db.check_member_last_stats(ctx.author.id):
                    
                    last_stats = self.db.get_member_last_stats(ctx.author.id)
                    if last_stats is None:
                        await ctx.respond(embed=self.err_msg.session_not_found())
                        return
                    last_stats = PlayerGlobalData.model_validate(last_stats)
                    session_timestamp = last_stats.timestamp
                    time_format = f'%H{self.text_obj.get().frequent.common.time_units.h} : %M{self.text_obj.get().frequent.common.time_units.m}'
                    now_time = datetime.now().timestamp()
                    passed_time = now_time - session_timestamp
                    try:
                        end_time = self.db.get_session_end_time(ctx.author.id)
                    except database.MemberNotFound:
                        await ctx.respond(
                            embed=self.inf_msg.custom(
                                Text().get(),
                                self.text_obj.get().frequent.info.player_not_registred,
                                )
                            )
                        return
                    
                    time_left = end_time - now_time
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
                        self.text_obj.get().cmds.session_state.items.started,
                        {
                            'time': TimeConverter.formatted_from_secs(int(passed_time), time_format),
                            'time_left': TimeConverter.formatted_from_secs(int(time_left), time_format),
                            'battles': str(battles_after - battles_before)
                        }
                    #     ('time', 'time_left', 'battles'),
                    #     (
                    #         TimeConverter.formatted_from_secs(int(passed_time), time_format),
                    #         TimeConverter.formatted_from_secs(int(time_left), time_format),
                    #         str(battles_after - battles_before)
                    #     )
                    # )
                    )
                    await ctx.respond(embed=self.inf_msg.session_state(text))
                else:
                    await ctx.respond(
                        embed=self.inf_msg.custom(
                            Text().get(),
                            self.text_obj.get().cmds.session_state.items.not_started,
                            colour='orange'
                            )
                        )
            else:
                await ctx.respond(
                    embed=self.inf_msg.custom(
                        Text().get(),
                        self.text_obj.get().cmds.session_state.info.player_not_registred,
                        colour='blue'
                        )
                    )
        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())


async def on_error(self, ctx: commands.Context, _):
        _log.error(traceback.format_exc())
        await ctx.respond(embed=self.inf_msg.cooldown_not_expired())

def setup(bot):
    for i in ['get_session', 'session_state']:
        getattr(Session, i).error(on_error)
    bot.add_cog(Session(bot))