from datetime import time, datetime
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
            default=0,
            description_localizations={
                'ru': 'TZ_Info',
                'pl': 'TZ_Info',
                'uk': 'TZ_Info'
            },
            min_value=0,
            max_value=12,
            required=False
            ),
        reset_time: Option(
            str,
            description='R_Time',
            default='00:00',
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
            member = self.db.get_member(ctx.author.id)
            session_settings = self.db.session_settings_get(ctx.author.id)
            session_settings.last_get = int(datetime.now(tz=pytz.utc).timestamp())
            session_settings.is_autosession = True
            session_settings.timezone = timezone
            session_settings.time_to_restart = reset_time if validate(reset_time) else '00:00'
            
            self.db.session_settings_set(session_settings)
            self.db.set_member_last_stats(ctx.author.id, member.last_stats)
            await ctx.respond(f'autosession_started, reset in <time> h')
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
            last_stats = await self.api.get_stats(member.nickname, member.region)
            session_settings = self.db.session_settings_get(ctx.author.id)
            session_settings.last_get = int(datetime.now(tz=pytz.utc).timestamp())
            session_settings.is_autosession = False
            self.db.session_settings_set()
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

            try:
                stats = await self.api.get_stats(member.nickname, member.region)
            except api.APIError:
                await ctx.respond(embed=self.err_msg.api_error())
                return

            last_stats = self.db.get_member_last_stats(member.id)

            if last_stats is None:
                await ctx.respond(embed=self.err_msg.session_not_found())
                return

            last_stats = PlayerGlobalData.model_validate(last_stats)

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
        
        if self.db.check_member(ctx.author.id):
            if self.db.check_member_last_stats(ctx.author.id):
                
                last_stats = self.db.get_member_last_stats(ctx.author.id)
                if last_stats is None:
                    await ctx.respond(embed=self.err_msg.session_not_found())
                    return
                last_stats = PlayerGlobalData.model_validate(last_stats)
                session_timestamp = last_stats.timestamp
                time_format = f'%H{Text().get().frequent.common.time_units.h} : %M{Text().get().frequent.common.time_units.m}'
                now_time = datetime.now().timestamp()
                passed_time = now_time - session_timestamp
                try:
                    end_time = self.db.get_session_end_time(ctx.author.id)
                except database.MemberNotFound:
                    await ctx.respond(
                        embed=self.inf_msg.custom(
                            Text().get(),
                            Text().get().frequent.info.player_not_registred,
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

                text = insert_data(
                    Text().get().cmds.session_state.items.started,
                    {
                        'time': TimeConverter.formatted_from_secs(int(passed_time), time_format),
                        'time_left': TimeConverter.formatted_from_secs(int(time_left), time_format),
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