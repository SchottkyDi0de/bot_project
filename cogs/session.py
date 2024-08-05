from datetime import datetime, timedelta
import traceback
import pytz

from discord import File, Option
from discord.ext import commands
from discord.commands import ApplicationContext

from lib.data_classes.member_context import MixedApplicationContext
from lib.utils.commands_wrapper import with_user_context_wrapper
from lib.utils.slot_info import get_formatted_slot_info
from lib.api.async_wotb_api import API
from lib.data_classes.db_player import AccountSlotsEnum, DBPlayer
from lib.data_parser.parse_data import get_session_stats
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.error_handler.common import hook_exceptions
from lib.image.session import ImageGenSession
from lib.locale.locale import Text
from lib.logger.logger import get_logger
from lib.utils.validators import validate
from lib.utils.bool_to_text import bool_handler
from lib.utils.time_converter import TimeConverter
from lib.utils.string_parser import insert_data
from lib.views.alt_views import UpdateSession


_log = get_logger(__file__, 'CogSessionLogger', 'logs/cog_session.log')


class Session(commands.Cog):
    cog_command_error = hook_exceptions(_log)

    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = PlayersDB()
        self.sdb = ServersDB()
        self.api = API()
        self.err_msg = ErrorMSG()
        self.inf_msg = InfoMSG()
    
    async def _generate_image(self, ctx: ApplicationContext, member: DBPlayer, slot: AccountSlotsEnum) -> File:
        game_account = await self.db.get_game_account(slot, member=member)

        stats = await self.api.get_stats(
            game_id=game_account.game_id,
            region=game_account.region,
            requested_by=member
        )

        last_stats = await self.db.get_last_stats(member=member, slot=slot)
        
        session_settings = game_account.session_settings
        session_settings.last_get = datetime.now(pytz.utc)
        server = await self.sdb.get_server(ctx)
        
        await self.db.set_session_settings(slot, member.id, session_settings)
        diff_stats = await get_session_stats(last_stats, stats)
        
        image = ImageGenSession().generate(
            data=game_account.last_stats,
            diff_data=diff_stats,
            player=member,
            server=server,
            slot=slot
        )

        server = await self.sdb.get_server(ctx)
        file = File(image, 'session.png')
        image.close()
        
        return file
        
    @commands.slash_command(
        guild_only=True,
        description=Text().get('en').cmds.start_autosession.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.start_autosession.descr.this,
            'pl': Text().get('pl').cmds.start_autosession.descr.this,
            'uk': Text().get('ua').cmds.start_autosession.descr.this
        }
    )
    @with_user_context_wrapper('start_autosession')
    async def start_autosession(
        self, 
        mixed_ctx: MixedApplicationContext,
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
            ),
        account: Option(
            int,
            description=Text().get().frequent.common.slot,
            description_localizations={
                'ru': Text().get('ru').frequent.common.slot,
                'pl': Text().get('pl').frequent.common.slot,
                'uk': Text().get('ua').frequent.common.slot
            },
            choices=[x.value for x in AccountSlotsEnum],
            required=True,
            default=None
            )
        ):
        ctx = mixed_ctx.ctx
        m_ctx = mixed_ctx.m_ctx
        await ctx.defer()
        
        game_account, member, account_slot = m_ctx.game_account, m_ctx.member, m_ctx.slot
        
        valid_time = validate(restart_time, 'time')
        now_time = datetime.now(tz=pytz.utc).replace(hour=0, minute=0, second=0)
        
        session_settings = game_account.session_settings
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
            
        last_stats = await self.api.get_stats(
            region=game_account.region, 
            game_id=game_account.game_id,
            requested_by=member
        )
        
        await self.db.start_session(
            slot=account_slot, 
            member_id=member.id, 
            last_stats=last_stats, 
            session_settings=session_settings
        )
        
        if valid_time or restart_time is None:
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    Text().get().cmds.start_autosession.info.started,
                    colour='green',
                    footer=get_formatted_slot_info(
                        slot=account_slot,
                        text=Text().get(),
                        game_account=game_account,
                        shorted=True,
                        clear_md=True
                    )
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
           
        
    @commands.slash_command(
        guild_only=True, 
        description=Text().get('en').cmds.start_session.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.start_session.descr.this,
            'pl': Text().get('pl').cmds.start_session.descr.this,
            'uk': Text().get('ua').cmds.start_session.descr.this
            }
        )
    @with_user_context_wrapper('start_session')
    async def start_session(
        self, 
        mixed_ctx: MixedApplicationContext,
        account: Option(
            int,
            description=Text().get().frequent.common.slot,
            description_localizations={
                'ru': Text().get('ru').frequent.common.slot,
                'pl': Text().get('pl').frequent.common.slot,
                'uk': Text().get('ua').frequent.common.slot
            },
            choices=[x.value for x in AccountSlotsEnum],
            required=True
            ),
        ):
        ctx = mixed_ctx.ctx
        m_ctx = mixed_ctx.m_ctx
        
        await ctx.defer()
        
        game_account, member, account_slot = m_ctx.game_account, m_ctx.member, m_ctx.slot
        
        last_stats = await self.api.get_stats(
            game_id=game_account.game_id,
            region=game_account.region,
            requested_by=member
        )
        
        session_settings = game_account.session_settings
        session_settings.last_get = datetime.now(tz=pytz.utc)
        session_settings.is_autosession = False
        
        await self.db.start_session(
            slot=account_slot, 
            member_id=member.id, 
            last_stats=last_stats, 
            session_settings=session_settings
        )
        
        await ctx.respond(embed=self.inf_msg.session_started()\
            .set_footer(
                text=get_formatted_slot_info(
                    slot=account_slot,
                    text=Text().get(),
                    game_account=game_account,
                    shorted=True,
                    clear_md=True
                )
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
    @with_user_context_wrapper('get_session', need_session=True)
    async def get_session(
        self, 
        mixed_ctx: MixedApplicationContext,
        account: Option(
            int,
            description=Text().get().frequent.common.slot,
            description_localizations={
                'ru': Text().get('ru').frequent.common.slot,
                'pl': Text().get('pl').frequent.common.slot,
                'uk': Text().get('ua').frequent.common.slot
            },
            choices=[x.value for x in AccountSlotsEnum],
            required=False,
            default=None
            )
        ):
        ctx = mixed_ctx.ctx
        m_ctx = mixed_ctx.m_ctx
        
        await ctx.defer()
        
        game_account, member, slot = m_ctx.game_account, m_ctx.member, m_ctx.slot
        server = await self.sdb.get_server(ctx)
        
        embed = self.inf_msg.custom(
            locale=Text().get(),
            colour='green',
            text=get_formatted_slot_info(
                slot=slot,
                text=Text().get(),
                game_account=game_account,
                shorted=True
            ),
            fields=[
                {
                    'name': Text().get().frequent.info.updated_at, 
                    'value': f'<t:{int(datetime.now(pytz.utc).timestamp())}:R>'
                }
            ]
        )
        view = UpdateSession(
            game_account=game_account, 
            player_id=member.id, 
            slot=slot, 
            text=Text().get(), 
            server=server
        ).get_view()
        file = await self._generate_image(ctx, member, slot)
        await ctx.respond(file=file, view=view, embed=embed)

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
    @with_user_context_wrapper('session_state')
    async def session_state(
        self, 
        mixed_ctx: MixedApplicationContext,
        account: Option(
            int,
            description=Text().get().frequent.common.slot,
            description_localizations={
                'ru': Text().get('ru').frequent.common.slot,
                'pl': Text().get('pl').frequent.common.slot,
                'uk': Text().get('ua').frequent.common.slot
            },
            choices=[x.value for x in AccountSlotsEnum],
            required=False,
            default=None
            )
        ):
        ctx = mixed_ctx.ctx
        m_ctx = mixed_ctx.m_ctx
        
        await ctx.defer()
        
        game_account, member, slot = m_ctx.game_account, m_ctx.member, m_ctx.slot
        
        if isinstance(member, bool):
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    Text().get().cmds.session_state.info.player_not_registred
                )
            )
            return
        
        last_stats = await self.db.get_last_stats(member=member, slot=slot)
        
        now_time = datetime.now(pytz.utc)
        session_settings = game_account.session_settings
        
        time_format =   f'%H:' \
                        f'%M'
        long_time_format = f'%D{Text().get().frequent.common.time_units.d} | ' \
                        f'%H:' \
                        f'%M'
        
        if session_settings.last_get is None or session_settings.time_to_restart is None:
            _log.error('last_get or time_to_restart is None')
            _log.error(traceback.format_exc())
            return
        
        restart_in = session_settings.time_to_restart - (now_time + timedelta(hours=session_settings.timezone))
        time_left = await self.db.get_session_end_time(member=member, slot=slot) - now_time
        session_time = now_time - last_stats.timestamp
        
        battles_before = last_stats.data.statistics.all.battles
        r_battles_before = last_stats.data.statistics.rating.battles
        battles_after, r_battles_after = await self.api.get_player_battles(last_stats.region, str(last_stats.id))
        
        diff_battles = battles_after - battles_before
        diff_r_battles = r_battles_after - r_battles_before

        text = insert_data(
            Text().get().cmds.session_state.items.started,
            {
                'is_autosession' : bool_handler(session_settings.is_autosession),
                'restart_in' : TimeConverter.formatted_from_secs(int(restart_in.total_seconds()), time_format),
                'update_time' : (session_settings.time_to_restart).strftime(time_format),
                'timezone' : session_settings.timezone,
                'time': TimeConverter.formatted_from_secs(int(session_time.total_seconds()), long_time_format),
                'time_left': TimeConverter.formatted_from_secs(int(time_left.total_seconds()), long_time_format),
                'battles': f'{diff_battles} | {diff_r_battles}'
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
        await ctx.respond(
            embed=self.inf_msg.session_state(text)\
                .set_footer(
                    text=get_formatted_slot_info(
                    slot=slot,
                    text=Text().get(),
                    game_account=game_account,
                    shorted=True,
                    clear_md=True
                    )
                )
            )


def setup(bot: commands.Bot):
    bot.add_cog(Session(bot))