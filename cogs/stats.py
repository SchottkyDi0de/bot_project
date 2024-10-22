from collections.abc import Callable
from datetime import datetime, timedelta
from functools import partial

from discord import File, InteractionContextType, Option, Bot
from discord.ext import commands
from discord.commands import ApplicationContext
import pytz

from lib.utils.selectors import account_selector, global_players_selector
from lib.data_classes.member_context import MixedApplicationContext
from lib.utils.commands_wrapper import with_user_context_wrapper
from lib.settings.settings import Config
from lib.image.common import ImageGenCommon
from lib.locale.locale import Text
from lib.api.async_wotb_api import API
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.data_classes.db_player import (
    AccountSlotsEnum, 
    DBPlayer, 
    HookStats, 
    HookStatsTriggers, 
    UsedCommand, 
    HookWatchFor
)
from lib.exceptions.api import NoPlayersFound
from lib.blacklist.blacklist import check_user
from lib.exceptions import api, data_parser
from lib.error_handler.common import hook_exceptions
from lib.data_classes.db_server import DBServer
from lib.logger.logger import get_logger
from lib.utils.nickname_handler import handle_nickname
from lib.utils.slot_info import get_formatted_slot_info
from lib.utils.string_parser import insert_data
from lib.utils.validators import NickTypes, validate
from lib.views.alt_views import HookOverride, HookDisable

_log = get_logger(__file__, 'CogStatsLogger', 'logs/cog_stats.log')
_config = Config().get()


class Stats(commands.Cog):
    cog_command_error = hook_exceptions(_log)

    def __init__(self, bot) -> None:
        self.bot = bot
        self.img_gen = ImageGenCommon()
        self.api = API()
        self.db = PlayersDB()
        self.sdb = ServersDB()
        self.inf_msg = InfoMSG()
        self.err_msg = ErrorMSG()
        
    @commands.slash_command(
        contexts=[InteractionContextType.guild],
        description=Text().get('en').cmds.stats.descr.this,
        description_localizations={
            'ru' : Text().get('ru').cmds.stats.descr.this,
            'pl' : Text().get('pl').cmds.stats.descr.this,
            'uk' : Text().get('ua').cmds.stats.descr.this
            }
        )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stats(
            self, 
            ctx: ApplicationContext,
            nick_or_id: Option(
                str,
                description=Text().get('en').frequent.common.nickname,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.nickname,
                    'pl': Text().get('pl').frequent.common.nickname,
                    'uk': Text().get('ua').frequent.common.nickname
                },
                required=True,
                autocomplete=global_players_selector
            ),
            region: Option(
                str,
                description=Text().get('en').frequent.common.region,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.region,
                    'pl': Text().get('pl').frequent.common.region,
                    'uk': Text().get('ua').frequent.common.region
                },
                choices=Config().get().default.available_regions,
                required=False
            ),
        ):
        await ctx.defer()
        await Text().load_from_context(ctx)
        await check_user(ctx)
        
        member = await self.db.check_member_exists(ctx.author.id, raise_error=False, get_if_exist=True)
        member = None if isinstance(member, bool) else member
        
        nickname_type = validate(nick_or_id, 'nickname')
        composite_nickname = handle_nickname(nick_or_id, nickname_type)
        
        if composite_nickname.region is not None:
            region = composite_nickname.region
        else:
            if region is None:
                await ctx.respond(
                    embed=self.err_msg.custom(
                        Text().get(),
                        text=Text().get().frequent.errors.reg_not_set
                    ),
                    ephemeral=True
                )
                return
        
        if member is not None:
            await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
        
        img = await self.get_stats(
            ctx, 
            region=region,
            nickname=composite_nickname.nickname,
            game_id=composite_nickname.player_id,
            requested_by=member,
            server=await self.sdb.get_server(ctx)
        )

        if img is not None:
            await ctx.respond(file=File(img, 'stats.png'))
            img.close()

    @commands.slash_command(
        contexts=[InteractionContextType.guild],
        description=Text().get('en').cmds.astats.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.astats.descr.this,
            'pl': Text().get('pl').cmds.astats.descr.this,
            'uk': Text().get('ua').cmds.astats.descr.this
            }
        )
    @commands.cooldown(1, 10, commands.BucketType.user)
    @with_user_context_wrapper('astats')
    async def astats(
        self,
        mixed_ctx: MixedApplicationContext,
        account: Option(
            str,
            description=Text().get('en').frequent.common.slot,
            description_localizations={
                'ru': Text().get('ru').frequent.common.slot,
                'pl': Text().get('pl').frequent.common.slot,
                'uk': Text().get('ua').frequent.common.slot
            },
            default=None,
            autocomplete=account_selector,
            ),
        ) -> None:
        ctx = mixed_ctx.ctx
        m_ctx = mixed_ctx.m_ctx
        
        server = await self.sdb.get_server(ctx)
        img = await self.get_stats(
            ctx,
            region=m_ctx.game_account.region,
            game_id=m_ctx.game_account.game_id, 
            slot=m_ctx.slot,
            server=server,
            requested_by=m_ctx.member
        )

        if img is not None:
            await ctx.respond(file=File(img, 'stats.png'))
            img.close()
        else:
            return
    
    @commands.slash_command(
        contexts=[InteractionContextType.guild],
        description=Text().get('en').cmds.hook_stats.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.hook_stats.descr.this,
            'pl': Text().get('pl').cmds.hook_stats.descr.this,
            'uk': Text().get('ua').cmds.hook_stats.descr.this
        }
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    @with_user_context_wrapper('hook_stats', premium=True)
    async def hook_stats(
        self, 
        mixed_ctx: MixedApplicationContext,
        stats_name: Option(
            str,
            description=Text().get('en').cmds.hook_stats.descr.sub_descr.stats_name,
            description_localizations={
                'ru': Text().get('ru').cmds.hook_stats.descr.sub_descr.stats_name,
                'pl': Text().get('pl').cmds.hook_stats.descr.sub_descr.stats_name,
                'uk': Text().get('ua').cmds.hook_stats.descr.sub_descr.stats_name
            },
            required=True,
            choices=[stats for stats in _config.image.available_stats],
        ),
        trigger: Option(
            str,
            description=Text().get('en').cmds.hook_stats.descr.sub_descr.trigger,
            description_localizations={
                'ru': Text().get('ru').cmds.hook_stats.descr.sub_descr.trigger,
                'pl': Text().get('pl').cmds.hook_stats.descr.sub_descr.trigger,
                'uk': Text().get('ua').cmds.hook_stats.descr.sub_descr.trigger
            },
            required=True,
            choices=[x.name for x in HookStatsTriggers],
        ),
        target_value: Option(
            float,
            description=Text().get('en').cmds.hook_stats.descr.sub_descr.target_value,
            description_localizations={
                'ru': Text().get('ru').cmds.hook_stats.descr.sub_descr.target_value,
                'pl': Text().get('pl').cmds.hook_stats.descr.sub_descr.target_value,
                'uk': Text().get('ua').cmds.hook_stats.descr.sub_descr.target_value
            },
            min_value=-10_000_000_000,
            max_value=10_000_000_000,
            required=True
        ),
        watch_for: Option(
            str,
            description=Text().get('en').cmds.hook_stats.descr.sub_descr.stats_type,
            description_localizations={
                'ru': Text().get('ru').cmds.hook_stats.descr.sub_descr.stats_type,
                'pl': Text().get('pl').cmds.hook_stats.descr.sub_descr.stats_type,
                'uk': Text().get('ua').cmds.hook_stats.descr.sub_descr.stats_type
            },
            required=True,
            choices=[x.value for x in HookWatchFor],
        ),
        account: Option(
            str,
            description=Text().get('en').frequent.common.slot,
            description_localizations={
                'ru': Text().get('ru').frequent.common.slot,
                'pl': Text().get('pl').frequent.common.slot,
                'uk': Text().get('ua').frequent.common.slot
            },
            default=None,
            autocomplete=partial(account_selector, session_required=True),
            ),
        target: Option(
            str,
            description=Text().get('en').cmds.hook_stats.descr.sub_descr.target,
            description_localizations={
                'ru': Text().get('ru').cmds.hook_stats.descr.sub_descr.target,
                'pl': Text().get('pl').cmds.hook_stats.descr.sub_descr.target,
                'uk': Text().get('ua').cmds.hook_stats.descr.sub_descr.target
            },
            autocomplete=global_players_selector,
            default='self'
            )
        ) -> None:
        ctx = mixed_ctx.ctx
        m_ctx = mixed_ctx.m_ctx
        
        target_override = False
        
        game_account, slot, member = m_ctx.game_account, m_ctx.slot, m_ctx.member
        
        if target != 'self':
            nickname_type = validate(target, 'nickname')
            composite_nickname = handle_nickname(target, nickname_type)
            if nickname_type is not NickTypes.COMPLETION:
                raise NoPlayersFound
            
            player_data = await self.api.get_player(composite_nickname.region, composite_nickname.nickname, ignore_lock=True)
            composite_nickname.player_id = player_data['account_id']
        
        if not target == 'self':
            target_override = True

        if target_override:
            last_stats = await self.api.get_stats(composite_nickname.region, composite_nickname.player_id, ignore_lock=True)
        else:
            last_stats = await self.api.get_stats(game_account.region, game_account.game_id, ignore_lock=True)
            
        old_hook = m_ctx.game_account.hook_stats
        
        hook = HookStats(
            active=True,
            last_stats=last_stats,
            stats_name=stats_name,
            stats_type='common',
            trigger=HookStatsTriggers[trigger].name,
            target_value=target_value,
            end_time=datetime.now(pytz.utc) + timedelta(days=2),
            target_game_id=composite_nickname.player_id if target_override else game_account.game_id,
            target_game_region=composite_nickname.region if target_override else game_account.region,
            target_nickname=composite_nickname.nickname if target_override else game_account.nickname,
            target_member_id=member.id,
            target_channel_id=ctx.channel.id,
            target_guild_id=ctx.guild.id,
            watch_for=watch_for,
            lang=Text().get_current_lang(),
        )
        
        if old_hook.active:
            view = HookOverride(
                text=Text().get(),
                member=member,
                game_account=game_account,
                slot=slot,
                hook=hook
            ).get_view()
            await ctx.respond(
                embed=InfoMSG().custom(
                    locale=Text().get(),
                    text=insert_data(
                        Text().get().cmds.hook_stats.warns.another_active_hook,
                        {
                            'stats_name' : old_hook.stats_name,
                            'trigger' : HookStatsTriggers[old_hook.trigger].value,
                            'value' : round(old_hook.target_value, 4),
                            'watch_for' : old_hook.watch_for,
                            'end_time' : f'<t:{int(old_hook.end_time.timestamp())}:R>'
                        }
                    ),
                    footer=get_formatted_slot_info(
                        slot, 
                        text=Text().get(),
                        game_account=game_account,
                        shorted=True,
                        clear_md=True
                    )
                ),
                view=view
            )
            return
        
        await self.db.setup_stats_hook(
            member_id=member.id,
            slot=slot,
            hook=hook
        )
        await ctx.respond(
            embed=InfoMSG().custom(
                locale=Text().get(),
                text=insert_data(
                    Text().get().cmds.hook_stats.info.success,
                    {
                        'stats_name' : hook.stats_name,
                        'trigger' : HookStatsTriggers[hook.trigger].value,
                        'value' : round(hook.target_value, 4),
                        'watch_for' : watch_for
                    }
                ),
                footer=get_formatted_slot_info(
                    slot, 
                    text=Text().get(),
                    game_account=game_account,
                    shorted=True,
                    clear_md=True
                )
            )
        )
        
    @commands.slash_command(
        contexts=[InteractionContextType.guild],
        description=Text().get('en').cmds.hook_stats.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.hook_stats.descr.this,
            'pl': Text().get('pl').cmds.hook_stats.descr.this,
            'uk': Text().get('ua').cmds.hook_stats.descr.this
        }
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    @with_user_context_wrapper('hook_stats_rating', premium=True)
    async def hook_stats_rating(
        self, 
        mixed_ctx: MixedApplicationContext, 
        stats_name: Option(
            str,
            description=Text().get('en').cmds.hook_stats.descr.sub_descr.stats_name,
            description_localizations={
                'ru': Text().get('ru').cmds.hook_stats.descr.sub_descr.stats_name,
                'pl': Text().get('pl').cmds.hook_stats.descr.sub_descr.stats_name,
                'uk': Text().get('ua').cmds.hook_stats.descr.sub_descr.stats_name
            },
            required=True,
            choices=[stats for stats in _config.image.available_rating_stats],
        ),
        trigger: Option(
            str,
            description=Text().get('en').cmds.hook_stats.descr.sub_descr.trigger,
            description_localizations={
                'ru': Text().get('ru').cmds.hook_stats.descr.sub_descr.trigger,
                'pl': Text().get('pl').cmds.hook_stats.descr.sub_descr.trigger,
                'uk': Text().get('ua').cmds.hook_stats.descr.sub_descr.trigger
            },
            required=True,
            choices=[x.name for x in HookStatsTriggers],
        ),
        target_value: Option(
            float,
            description=Text().get('en').cmds.hook_stats.descr.sub_descr.target_value,
            description_localizations={
                'ru': Text().get('ru').cmds.hook_stats.descr.sub_descr.target_value,
                'pl': Text().get('pl').cmds.hook_stats.descr.sub_descr.target_value,
                'uk': Text().get('ua').cmds.hook_stats.descr.sub_descr.target_value
            },
            min_value=-10_000_000_000,
            max_value=10_000_000_000,
            required=True
        ),
        watch_for: Option(
            str,
            description=Text().get('en').cmds.hook_stats.descr.sub_descr.stats_type,
            description_localizations={
                'ru': Text().get('ru').cmds.hook_stats.descr.sub_descr.stats_type,
                'pl': Text().get('pl').cmds.hook_stats.descr.sub_descr.stats_type,
                'uk': Text().get('ua').cmds.hook_stats.descr.sub_descr.stats_type
            },
            required=True,
            choices=[x.value for x in HookWatchFor],
        ),
        account: Option(
            str,
            description=Text().get('en').frequent.common.slot,
            description_localizations={
                'ru': Text().get('ru').frequent.common.slot,
                'pl': Text().get('pl').frequent.common.slot,
                'uk': Text().get('ua').frequent.common.slot
            },
            default=None,
            autocomplete=partial(account_selector, session_required=True),
            ),
        ) -> None:
        ctx = mixed_ctx.ctx
        m_ctx = mixed_ctx.m_ctx

        game_account, member, slot = m_ctx.game_account, m_ctx.member, m_ctx.slot
        old_hook = game_account.hook_stats
        
        hook = HookStats(
            active=True,
            stats_name=stats_name,
            stats_type='rating',
            trigger=HookStatsTriggers[trigger].name,
            target_value=target_value,
            end_time=datetime.now(pytz.utc) + timedelta(days=2),
            target_member_id=member.id,
            target_channel_id=ctx.channel.id,
            target_guild_id=ctx.guild.id,
            watch_for=watch_for,
            lang=Text().get_current_lang(),
        )
        
        if old_hook.active:
            view = HookOverride(
                text=Text().get(),
                member=member,
                game_account=game_account,
                slot=slot,
                hook=hook
            ).get_view()
            await ctx.respond(
                embed=InfoMSG().custom(
                    locale=Text().get(),
                    text=insert_data(
                        Text().get().cmds.hook_stats.warns.another_active_hook,
                        {
                            'stats_name' : old_hook.stats_name,
                            'trigger' : HookStatsTriggers[old_hook.trigger].value,
                            'value' : round(old_hook.target_value, 4),
                            'watch_for' : old_hook.watch_for,
                            'end_time' : f'<t:{int(old_hook.end_time.timestamp())}:R>'
                        }
                    ),
                    footer=get_formatted_slot_info(
                        slot, 
                        text=Text().get(),
                        game_account=game_account,
                        shorted=True,
                        clear_md=True
                    )
                ),
                view=view
            )
            return
        
        await self.db.setup_stats_hook(
            member_id=member.id,
            slot=slot,
            hook=hook
        )
        await ctx.respond(
            embed=InfoMSG().custom(
                locale=Text().get(),
                text=insert_data(
                    Text().get().cmds.hook_stats.info.success,
                    {
                        'stats_name' : hook.stats_name,
                        'trigger' : HookStatsTriggers[hook.trigger].value,
                        'value' : round(hook.target_value, 4),
                        'watch_for' : watch_for
                    }
                ),
                footer=get_formatted_slot_info(
                    slot, 
                    text=Text().get(),
                    game_account=game_account,
                    shorted=True,
                    clear_md=True
                )
            )
        )
        
    @commands.slash_command(
        contexts=[InteractionContextType.guild],
        description=Text().get('en').cmds.stats.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.stats.descr.this,
            'pl': Text().get('pl').cmds.stats.descr.this,
            'uk': Text().get('ua').cmds.stats.descr.this
        }
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    @with_user_context_wrapper('hook_status')
    async def hook_status(
            self,
            mixed_ctx: MixedApplicationContext,
            account: Option(
                str,
                description=Text().get('en').frequent.common.slot,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.slot,
                    'pl': Text().get('pl').frequent.common.slot,
                    'uk': Text().get('ua').frequent.common.slot
                },
                default=None,
                autocomplete=account_selector,
            ),
        ):
        ctx = mixed_ctx.ctx
        m_ctx = mixed_ctx.m_ctx

        game_account, member, slot = m_ctx.game_account, m_ctx.member, m_ctx.slot
        hook = game_account.hook_stats
        
        if hook.active:
            view = HookDisable(
                text=Text().get(),
                member=member,
                slot=slot,
                game_account=game_account,
            ).get_view()
            await ctx.respond(
                embed=InfoMSG().custom(
                    locale=Text().get(),
                    text=insert_data(
                        Text().get().cmds.hook_state.info.active,
                        {
                            'target_player' : f'{hook.target_nickname} | {hook.target_game_region.upper()}',
                            'watch_for' : hook.watch_for,
                            'stats_name' : hook.stats_name,
                            'trigger' : HookStatsTriggers[hook.trigger].value,
                            'value' : round(hook.target_value, 4),
                            'end_time' : f'<t:{int(hook.end_time.timestamp())}:R>'
                        }
                    ),
                    footer=get_formatted_slot_info(
                        slot,
                        text=Text().get(),
                        game_account=game_account,
                        shorted=True,
                        clear_md=True
                    )
                ),
                view=view
            )
            return
        
        await ctx.respond(
            embed=InfoMSG().custom(
                locale=Text().get(),
                text=Text().get().cmds.hook_state.info.inactive,
                footer=get_formatted_slot_info(
                    slot,
                    text=Text().get(),
                    game_account=game_account,
                    shorted=True,
                    clear_md=True
                )
            )
        )
        

    
    async def get_stats(
            self, 
            ctx: ApplicationContext, 
            region: str,
            server: DBServer | None = None,
            slot: AccountSlotsEnum | None = None,
            game_id: int | None = None,
            nickname: str | None = None,
            requested_by: DBPlayer | None = None
        ):
        exception = None
        real_exc = None
        try:
            data = await self.api.get_stats(
                game_id=game_id,
                search=nickname,
                region=region,
                requested_by=requested_by
                )
        except* api.EmptyDataError:
            exception = 'unknown_error'
        except* api.NeedMoreBattlesError:
            exception = 'need_more_battles'
        except* api.UncorrectName:
            exception = 'uncorrect_name'
        except* api.UncorrectRegion:
            exception = 'uncorrect_region'
        except* api.NoPlayersFound:
            exception = 'player_not_found'
        except* data_parser.DataParserError:
            exception = 'parser_error'
        except* api.LockedPlayer:
            exception = 'locked_player'
        except* api.APIError as e:
            exception = 'api_error'
            real_exc = e.exceptions[0].real_exc
            
        if exception is not None:
            embed_func: Callable = getattr(self.err_msg, exception)
            if embed_func.__name__ == 'api_error':
                await ctx.respond(embed=embed_func(real_exc=real_exc))
            else:
                await ctx.respond(embed=embed_func())
        else:
            img_data = self.img_gen.generate(
                data=data,
                server=server,
                member=requested_by,
                slot=slot
            )
            return img_data


def setup(bot: Bot):
    bot.add_cog(Stats(bot))
