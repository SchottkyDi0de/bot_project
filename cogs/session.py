from datetime import datetime, timedelta
import traceback
import pytz

from discord import File, Option
from discord.ext import commands

from lib.api.async_wotb_api import API
from lib.blacklist.blacklist import check_user
from lib.data_classes.api_data import PlayerGlobalData
from lib.data_classes.db_player import SessionSettings
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
from lib.utils.time_validator import validate
from lib.utils.bool_to_text import bool_handler


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
        description='Autosession start',
        description_localizations={
            'ru': 'Autosession start',
            'pl': 'Autosession start',
            'uk': 'Autosession start'
        }
    )
    async def start_autosession(
        self, 
        ctx: commands.Context,
        timezone: Option(
            int,
            description='TZ_Info',
            default=None,
            description_localizations={
                'ru': 'TZ_Info',
                'pl': 'TZ_Info',
                'uk': 'TZ_Info'
            },
            min_value=0,
            max_value=12,
            required=False
            ),
        restart_time: Option(
            str,
            description='R_Time',
            default=None,
            description_localizations={
                'ru': 'R_Time',
                'pl': 'R_Time',
                'uk': 'R_Time'
            },
            lenght=5,
            required=False
            )
        ):
        Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()
        
        if self.db.check_member(ctx.author.id):
            valid_time = validate(restart_time)
            now_time = datetime.now(tz=pytz.utc).replace(hour=0, minute=0, second=0)
            member = self.db.get_member(ctx.author.id)
            
            session_settings = self.db.get_member_session_settings(ctx.author.id)
            session_settings.last_get = datetime.now(tz=pytz.utc)
            session_settings.is_autosession = True
            
            if timezone is not None:
                session_settings.timezone = timezone
            
            if valid_time:
                session_settings.time_to_restart = (
                    now_time + timedelta(
                        seconds=TimeConverter.secs_from_str_time(restart_time)
                        )
                )
                
            try:
                last_stats = await self.api.get_stats(region=member.region, game_id=member.game_id)
            except APIError:
                await ctx.respond(embed=self.err_msg.api_error())
                _log.error(traceback.format_exc())
                return
            
            self.db.start_autosession(ctx.author.id, last_stats, session_settings)
            if valid_time or restart_time is None:
                await ctx.respond(
                    embed=self.inf_msg.custom(
                        Text().get(),
                        Text().get().cmds.start_autosession.info.started,
                        colour='green'
                    )
                )
            else:
                await ctx.respond(
                    embed=self.inf_msg.custom(
                        Text().get(),
                        (
                            insert_data(
                                Text().get().cmds.start_autosession.errors.uncorrect_r_time,
                                {'time': restart_time}
                                ) + 
                            '\n\n' +
                            Text().get().cmds.start_autosession.info.started
                        ),
                        title=Text().get().frequent.info.warning,
                        colour='orange'
                    )
                )
        else:
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    Text().get().cmds.start_session.info.player_not_registred
                )
            )
        
    @commands.slash_command(
        guild_only=True, 
        description=Text().get().cmds.start_session.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.start_session.descr.this,
            'pl': Text().get('pl').cmds.start_session.descr.this,
            'uk': Text().get('ua').cmds.start_session.descr.this
            }
        )
    async def start_session(self, ctx: commands.Context):
        Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()

        if self.db.check_member(ctx.author.id):
            member = self.db.get_member(ctx.author.id)
            last_stats = await self.api.get_stats(game_id=member.game_id, region=member.region)
            session_settings = self.db.get_member_session_settings(ctx.author.id)
            session_settings.last_get = datetime.now(tz=pytz.utc)
            session_settings.is_autosession = False
            
            self.db.set_member_session_settings(ctx.author.id, session_settings)
            self.db.set_member_last_stats(ctx.author.id, last_stats.model_dump())
            await ctx.respond(embed=self.inf_msg.session_started())
        else:
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    Text().get().cmds.start_session.info.player_not_registred
                )
            )

    @commands.slash_command(
            guild_only=True, 
            description=Text().get().cmds.get_session.descr.this,
            description_localizations={
                'ru': Text().get('ru').cmds.get_session.descr.this,
                'pl': Text().get('pl').cmds.get_session.descr.this,
                'uk': Text().get('ua').cmds.get_session.descr.this
                }
            )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def get_session(self, ctx: commands.Context):
        Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()

        if self.db.check_member(ctx.author.id):
            member = self.db.get_member(ctx.author.id)
            image_settings = self.db.get_image_settings(ctx.author.id)
            server_settings = self.sdb.get_server_settings(ctx)
            session_settings = self.db.get_member_session_settings(ctx.author.id)

            try:
                stats = await self.api.get_stats(game_id=member.game_id, region=member.region)
            except api.APIError:
                await ctx.respond(embed=self.err_msg.api_error())
                _log.error(traceback.format_exc())
                return

            try:
                last_stats = self.db.get_member_last_stats(member.id)
            except database.LastStatsNotFound:
                ctx.respond(self.err_msg.session_not_found())
                return
            
            session_settings.last_get = datetime.now(pytz.utc)
            self.db.set_member_session_settings(ctx.author.id, session_settings)

            try:
                diff_stats = get_session_stats(last_stats, stats)
            except data_parser.NoDiffData:
                await ctx.respond(embed=self.err_msg.session_not_updated())
                return
            
            image = ImageGen().generate(stats, diff_stats, ctx, image_settings, server_settings)
            await ctx.respond(file=File(image, 'session.png'))
            return

        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                Text().get().cmds.get_session.info.player_not_registred,
                colour='orange'
                )
            )

    @commands.slash_command(
            guild_only=True, 
            description='None',
            description_localizations={
                'ru' : Text().get('ru').cmds.session_state.descr.this,
                'pl' : Text().get('pl').cmds.session_state.descr.this,
                'uk' : Text().get('ua').cmds.session_state.descr.this
                }
            )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def session_state(self, ctx: commands.Context):
        Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()
        
        if self.db.check_member(ctx.author.id):
            if self.db.check_member_last_stats(ctx.author.id):
                self.db.validate_session(ctx.author.id)
                now_time = datetime.now(pytz.utc)
                
                try:
                    last_stats = self.db.get_member_last_stats(ctx.author.id)
                    session_settings = self.db.get_member_session_settings(ctx.author.id)
                except api.APIError:
                    _log.error(traceback.format_exc())
                    await ctx.respond(embed=self.err_msg.api_error())
                    return
                
                
                time_format = f'%H:' \
                                f'%M'
                long_time_format = f'%D{Text().get().frequent.common.time_units.d} | ' \
                                f'%H:' \
                                f'%M'
                
                if session_settings.last_get is None or session_settings.time_to_restart is None:
                    _log.error('last_get or time_to_restart is None')
                    _log.error(traceback.format_exc())
                    raise ValueError()
                
                restart_in = session_settings.time_to_restart - (now_time + timedelta(hours=session_settings.timezone))
                time_left = self.db.get_session_end_time(ctx.author.id) - now_time
                session_time = now_time - last_stats.timestamp
                
                try:
                    battles_before = last_stats.data.statistics.all.battles
                    battles_after = await self.api.get_player_battles(last_stats.region, str(last_stats.id))
                except APIError:
                    _log.error(traceback.format_exc())
                    await ctx.respond(embed=self.err_msg.api_error())
                    return

                text = insert_data(
                    Text().get().cmds.session_state.items.started,
                    {
                        'is_autosession' : bool_handler(session_settings.is_autosession),
                        'restart_in' : TimeConverter.formatted_from_secs(int(restart_in.total_seconds()), time_format),
                        'update_time' : (session_settings.time_to_restart).strftime(time_format),
                        'timezone' : session_settings.timezone,
                        'time': TimeConverter.formatted_from_secs(int(session_time.total_seconds()), long_time_format),
                        'time_left': TimeConverter.formatted_from_secs(int(time_left.total_seconds()), long_time_format),
                        'battles': str(battles_after - battles_before)
                    }
                ) if session_settings.is_autosession else \
                    insert_data(
                    Text().get().cmds.session_state.items.started,
                    {
                        'is_autosession' : bool_handler(session_settings.is_autosession),
                        'restart_in' : '--:--',
                        'update_time' : (session_settings.time_to_restart).strftime(time_format),
                        'timezone' : session_settings.timezone,
                        'time': TimeConverter.formatted_from_secs(int(session_time.total_seconds()), long_time_format),
                        'time_left': TimeConverter.formatted_from_secs(int(time_left.total_seconds()), long_time_format),
                        'battles': str(battles_after - battles_before)
                    }
                )
                await ctx.respond(embed=self.inf_msg.session_state(text))
            else:
                await ctx.respond(
                    embed=self.inf_msg.custom(
                        Text().get(),
                        Text().get().cmds.session_state.items.not_started,
                        colour='orange'
                        )
                    )
        else:
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    Text().get().cmds.session_state.info.player_not_registred,
                    colour='blue'
                    )
                )
            
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(embed=self.inf_msg.cooldown_not_expired())
        elif isinstance(error, UserBanned):
            await ctx.respond(embed=self.err_msg.user_banned())
        else:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())

def setup(bot):
    bot.add_cog(Session(bot))