from datetime import datetime, timedelta
import traceback
import pytz

from discord import File, Option, Embed
from discord.ext import commands
from discord.commands import ApplicationContext

from lib.api.async_wotb_api import API
from lib.blacklist.blacklist import check_user
from lib.data_parser.parse_data import get_session_stats
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.exceptions.error_handler.error_handler import error_handler
from lib.image.session import ImageGen
from lib.locale.locale import Text
from lib.logger.logger import get_logger
from lib.utils.validators import validate
from lib.utils.bool_to_text import bool_handler
from lib.utils.views import ViewMeta
from lib.utils.time_converter import TimeConverter
from lib.utils.string_parser import insert_data


_log = get_logger(__file__, 'CogSessionLogger', 'logs/cog_session.log')


class Session(commands.Cog):
    cog_command_error = error_handler(_log)

    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = PlayersDB()
        self.sdb = ServersDB()
        self.api = API()
        self.err_msg = ErrorMSG()
        self.inf_msg = InfoMSG()
    
    async def _generate_image(self, ctx: ApplicationContext) -> File | Embed:
        member = self.db.get_member(ctx.author.id)
        image_settings = self.db.get_image_settings(ctx.author.id)
        server_settings = self.sdb.get_server_settings(ctx)
        session_settings = self.db.get_member_session_settings(ctx.author.id)

        stats = await self.api.get_stats(game_id=member.game_id, region=member.region)

        last_stats = self.db.get_member_last_stats(member.id)
            
        session_settings.last_get = datetime.now(pytz.utc)
        self.db.set_member_session_settings(ctx.author.id, session_settings)

        diff_stats = get_session_stats(last_stats, stats)
            
        return File(ImageGen().generate(stats, diff_stats, ctx, image_settings, server_settings), 'session.png')
        
    @commands.slash_command(
        guild_only=True,
        description=Text().get('en').cmds.start_autosession.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.start_autosession.descr.this,
            'pl': Text().get('pl').cmds.start_autosession.descr.this,
            'uk': Text().get('ua').cmds.start_autosession.descr.this
        }
    )
    async def start_autosession(
        self, 
        ctx: ApplicationContext,
        timezone: Option(
            int,
            description=Text().get('en').cmds.start_autosession.descr.sub_descr.timezone,
            default=None,
            description_localizations={
                'ru': Text().get('ru').cmds.start_autosession.descr.sub_descr.timezone,
                'pl': Text().get('pl').cmds.start_autosession.descr.sub_descr.timezone,
                'uk': Text().get('ua').cmds.start_autosession.descr.sub_descr.timezone
            },
            min_value=0,
            max_value=12,
            required=False
            ),
        restart_time: Option(
            str,
            description=Text().get('en').cmds.start_autosession.descr.sub_descr.restart_time,
            default=None,
            description_localizations={
                'ru': Text().get('ru').cmds.start_autosession.descr.sub_descr.restart_time,
                'pl': Text().get('pl').cmds.start_autosession.descr.sub_descr.restart_time,
                'uk': Text().get('ua').cmds.start_autosession.descr.sub_descr.restart_time
            },
            length=5,
            required=False
            )
        ):
        Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()
        
        if self.db.check_member(ctx.author.id):
            valid_time = validate(restart_time, 'time')
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
                
            last_stats = await self.api.get_stats(region=member.region, game_id=member.game_id)
            
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
        description=Text().get('en').cmds.start_session.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.start_session.descr.this,
            'pl': Text().get('pl').cmds.start_session.descr.this,
            'uk': Text().get('ua').cmds.start_session.descr.this
            }
        )
    async def start_session(self, ctx: ApplicationContext):
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
            description=Text().get('en').cmds.get_session.descr.this,
            description_localizations={
                'ru': Text().get('ru').cmds.get_session.descr.this,
                'pl': Text().get('pl').cmds.get_session.descr.this,
                'uk': Text().get('ua').cmds.get_session.descr.this
                }
            )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def get_session(self, ctx: ApplicationContext):
        Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()

        if self.db.check_member(ctx.author.id):
            generate_res = await self._generate_image(ctx)
            if isinstance(generate_res, File):
                await ctx.respond(file=generate_res, view=ViewMeta(bot=self.bot, ctx=ctx, type='session', session_self=self))
            else:
                await ctx.respond(embed=generate_res)
        else:
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    Text().get().cmds.get_session.info.player_not_registred,
                    colour='orange'
                    )
                )

    @commands.slash_command(
            guild_only=True, 
            description=Text().get('en').cmds.session_state.descr.this,
            description_localizations={
                'ru' : Text().get('ru').cmds.session_state.descr.this,
                'pl' : Text().get('pl').cmds.session_state.descr.this,
                'uk' : Text().get('ua').cmds.session_state.descr.this
                }
            )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def session_state(self, ctx: ApplicationContext):
        Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()
        
        if self.db.check_member(ctx.author.id):
            if self.db.check_member_last_stats(ctx.author.id):
                self.db.validate_session(ctx.author.id)
                now_time = datetime.now(pytz.utc)
                
                last_stats = self.db.get_member_last_stats(ctx.author.id)
                session_settings = self.db.get_member_session_settings(ctx.author.id)
                
                
                time_format = f'%H:' \
                                f'%M'
                long_time_format = f'%D{Text().get().frequent.common.time_units.d} | ' \
                                f'%H:' \
                                f'%M'
                
                if session_settings.last_get is None or session_settings.time_to_restart is None:
                    _log.error('last_get or time_to_restart is None')
                    _log.error(traceback.format_exc())
                    return
                
                restart_in = session_settings.time_to_restart - (now_time + timedelta(hours=session_settings.timezone))
                time_left = self.db.get_session_end_time(ctx.author.id) - now_time
                session_time = now_time - last_stats.timestamp
                
                battles_before = last_stats.data.statistics.all.battles
                battles_after = await self.api.get_player_battles(last_stats.region, str(last_stats.id))

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


def setup(bot):
    bot.add_cog(Session(bot))