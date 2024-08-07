from discord.ui import View, Button
from discord import InteractionContextType, Option
from discord.ext import commands
from webcolors import rgb_to_hex

from lib.utils.commands_wrapper import with_user_context_wrapper
from lib.data_classes.member_context import MixedApplicationContext
from lib.data_classes.db_player import AccountSlotsEnum, WidgetSettings
from lib.database.players import PlayersDB
from lib.embeds.info import InfoMSG
from lib.error_handler.common import hook_exceptions
from lib.locale.locale import Text
from lib.logger.logger import get_logger
from lib.settings.settings import Config
from lib.utils.color_converter import get_tuple_from_color
from lib.utils.string_parser import insert_data
from lib.image.utils.color_validator import color_validate
from lib.utils.slot_info import get_formatted_slot_info

_config = Config().get()
_log = get_logger(__file__, 'SessionWidgetLogger', 'logs/session_widget.log')

class SessionWidget(commands.Cog):
    cog_command_error = hook_exceptions(_log)
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pdb = PlayersDB()
        self.inf_msg = InfoMSG()

    @commands.slash_command(
        contexts=[InteractionContextType.guild],
        description=Text().get('en').cmds.session_widget.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.session_widget.descr.this,
            'pl': Text().get('pl').cmds.session_widget.descr.this,
            'uk': Text().get('ua').cmds.session_widget.descr.this
        }
    )
    @with_user_context_wrapper('session_widget', need_session=True)
    async def session_widget(
        self, 
        mixed_ctx: MixedApplicationContext,
        account: Option(
            int,
            description=Text().get('en').frequent.common.slot,
            description_localizations={
                'ru': Text().get('ru').frequent.common.slot,
                'pl': Text().get('pl').frequent.common.slot,
                'uk': Text().get('ua').frequent.common.slot
            },
            required=False,
            default=None,
            choices=[x.value for x in AccountSlotsEnum]
            )
        ):
        ctx = mixed_ctx.ctx
        m_ctx = mixed_ctx.m_ctx
        
        game_account, member, slot = m_ctx.game_account, m_ctx.member, m_ctx.slot
        
        _log.debug(f'Sending session widget to {member.id} in slot {slot.name}...')
        url = insert_data(
            _config.session_widget.url,
            {
                'user_id' : member.id,
                'lang' : Text().get_current_lang(),
                'slot' : slot.value
            }
        )
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=insert_data(Text().get().cmds.session_widget.info.success, {'link': url}),
                colour='green',
                footer=get_formatted_slot_info(
                    slot=slot,
                    text=Text().get(),
                    game_account=game_account,
                    shorted=True,
                    clear_md=True
                )
            ),
            view=View(
                Button(
                    label=Text().get().cmds.session_widget.items.btn,
                    url=url
                )
            ),
            ephemeral=True
        )
    
    @commands.slash_command(
        contexts=[InteractionContextType.guild],
        description=Text().get('en').cmds.session_widget_settings.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.session_widget_settings.descr.this,
            'pl': Text().get('pl').cmds.session_widget_settings.descr.this,
            'uk': Text().get('ua').cmds.session_widget_settings.descr.this
        }
    )
    @with_user_context_wrapper('widget_settings')
    async def widget_settings(
        self, 
        mixed_ctx: MixedApplicationContext,
        disable_bg: Option(
            bool,
            description=Text().get('en').cmds.session_widget_settings.items.disable_bg,
            description_localizations={
                'ru': Text().get('ru').cmds.session_widget_settings.items.disable_bg,
                'pl': Text().get('pl').cmds.session_widget_settings.items.disable_bg,
                'uk': Text().get('ua').cmds.session_widget_settings.items.disable_bg
                },
            required=False
            ),
        disable_nickname: Option(
            bool,
            description=Text().get('en').cmds.session_widget_settings.items.disable_nickname,
            description_localizations={
                'ru': Text().get('ru').cmds.session_widget_settings.items.disable_nickname,
                'pl': Text().get('pl').cmds.session_widget_settings.items.disable_nickname,
                'uk': Text().get('ua').cmds.session_widget_settings.items.disable_nickname
            },
            required=False
        ),
        max_stats_blocks: Option(
            int,
            description=Text().get('en').cmds.session_widget_settings.items.max_stats_blocks,
            description_localizations={
                'ru': Text().get('ru').cmds.session_widget_settings.items.max_stats_blocks,
                'pl': Text().get('pl').cmds.session_widget_settings.items.max_stats_blocks,
                'uk': Text().get('ua').cmds.session_widget_settings.items.max_stats_blocks
            },
            min_value=1,
            max_value=3,
            required=False
        ),
        max_stats_small_blocks: Option(
            int,
            description=Text().get('en').cmds.session_widget_settings.items.max_stats_small_blocks,
            description_localizations={
                'ru': Text().get('ru').cmds.session_widget_settings.items.max_stats_small_blocks,
                'pl': Text().get('pl').cmds.session_widget_settings.items.max_stats_small_blocks,
                'uk': Text().get('ua').cmds.session_widget_settings.items.max_stats_small_blocks
            },
            min_value=0,
            max_value=2,
            required=False
        ),
        update_time: Option(
            int,
            description=Text().get('en').cmds.session_widget_settings.items.update_per_seconds,
            description_localizations={
                'ru': Text().get('ru').cmds.session_widget_settings.items.update_per_seconds,
                'pl': Text().get('pl').cmds.session_widget_settings.items.update_per_seconds,
                'uk': Text().get('ua').cmds.session_widget_settings.items.update_per_seconds
            },
            min_value=30,
            max_value=360,
            required=False
        ),
        background_transparency: Option(
            float,
            description=Text().get('en').cmds.session_widget_settings.items.background_transparency,
            description_localizations={
                'ru': Text().get('ru').cmds.session_widget_settings.items.background_transparency,
                'pl': Text().get('pl').cmds.session_widget_settings.items.background_transparency,
                'uk': Text().get('ua').cmds.session_widget_settings.items.background_transparency
            },
            min_value=0,
            max_value=100,
            required=False
        ),
        disable_main_stats_block: Option(
            bool,
            description=Text().get('en').cmds.session_widget_settings.items.disable_main_stats_block,
            description_localizations={
                'ru': Text().get('ru').cmds.session_widget_settings.items.disable_main_stats_block,
                'pl': Text().get('pl').cmds.session_widget_settings.items.disable_main_stats_block,
                'uk': Text().get('ua').cmds.session_widget_settings.items.disable_main_stats_block
            },
            required=False
        ),
        use_bg_for_stats_blocks: Option(
            bool,
            description=Text().get('en').cmds.session_widget_settings.items.use_bg_for_stats_blocks,
            description_localizations={
                'ru': Text().get('ru').cmds.session_widget_settings.items.use_bg_for_stats_blocks,
                'pl': Text().get('pl').cmds.session_widget_settings.items.use_bg_for_stats_blocks,
                'uk': Text().get('ua').cmds.session_widget_settings.items.use_bg_for_stats_blocks
            },
            required=False
        ),
        adaptive_width: Option(
            bool,
            description=Text().get('en').cmds.session_widget_settings.items.adaptive_width,
            description_localizations={
                'ru': Text().get('ru').cmds.session_widget_settings.items.adaptive_width,
                'pl': Text().get('pl').cmds.session_widget_settings.items.adaptive_width,
                'uk': Text().get('ua').cmds.session_widget_settings.items.adaptive_width
            },
            required=False
        ),
        stats_block_color: Option(
            str,
            description=Text().get('en').cmds.session_widget_settings.items.stats_block_color,
            description_localizations={
                'ru': Text().get('ru').cmds.session_widget_settings.items.stats_block_color,
                'pl': Text().get('pl').cmds.session_widget_settings.items.stats_block_color,
                'uk': Text().get('ua').cmds.session_widget_settings.items.stats_block_color
            },
            required=False
        ),
        account: Option(
            int,
            description=Text().get('en').frequent.common.slot,
            description_localizations={
                'ru': Text().get('ru').frequent.common.slot,
                'pl': Text().get('pl').frequent.common.slot,
                'uk': Text().get('ua').frequent.common.slot
            },
            required=False,
            default=None,
            choices=[x.value for x in AccountSlotsEnum]
            )
        ):
        ctx = mixed_ctx.ctx
        m_ctx = mixed_ctx.m_ctx
        
        game_account, member, slot = m_ctx.game_account, m_ctx.member, m_ctx.slot
        widget_settings = await self.pdb.get_widget_settings(slot=slot, member=member)
        
        current_settings = {
            'adaptive_width': adaptive_width,
            'stats_block_color': stats_block_color,
            'use_bg_for_stats_blocks': use_bg_for_stats_blocks,
            'disable_main_stats_block': disable_main_stats_block,
            'background_transparency': background_transparency,
            'update_time': update_time,
            'max_stats_small_blocks': max_stats_small_blocks,
            'max_stats_blocks': max_stats_blocks,
            'disable_nickname': disable_nickname,
            'disable_bg': disable_bg
        }
        set_values_count = 0
        color_error_data = []
        color_error = False
        for key, value in current_settings.items():
            if value is None:
                current_settings[key] = getattr(widget_settings, key)
                continue
            if key == 'stats_block_color':
                validation_res = color_validate(value)
                if validation_res is not None:
                    set_values_count += 1
                    if validation_res[1] == 'hex':
                        current_settings[key] = value
                    else:
                        current_settings[key] = rgb_to_hex(get_tuple_from_color(value))
                else:
                    color_error = True
                    color_error_data.append({'param_name': key, 'value': value})
            if key == 'background_transparency':
                current_settings[key] = value / 100
                set_values_count += 1
            else:
                set_values_count += 1
                current_settings[key] = value
        
        
        if color_error:
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    title=Text().get().frequent.info.warning,
                    text=insert_data(
                        Text().get().cmds.image_settings.errors.color_error,
                        *color_error_data
                        ),
                    colour='orange',
                    footer=Text().get().cmds.image_settings.items.color_error_footer
                ).add_field(
                    name=Text().get().frequent.info.info,
                    value=Text().get().cmds.image_settings.items.color_error_note
                )
            )
            return
        
        if set_values_count == 0:
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    text=Text().get().cmds.session_widget_settings.errors.nothing_changed,
                    colour='orange'
                )
            )
            return
        
        await self.pdb.set_widget_settings(
            slot=slot, 
            member_id=member.id, 
            settings=WidgetSettings().model_validate(current_settings)
        )
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.session_widget_settings.info.success,
                colour='green',
                footer=get_formatted_slot_info(
                    slot=slot,
                    text=Text().get(),
                    game_account=game_account,
                    shorted=True,
                    clear_md=True
                )
            )
        )
    
    @commands.slash_command(
        contexts=[InteractionContextType.guild],
        description=Text().get('en').cmds.session_widget_settings_reset.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.session_widget_settings_reset.descr.this,
            'pl': Text().get('pl').cmds.session_widget_settings_reset.descr.this,
            'uk': Text().get('ua').cmds.session_widget_settings_reset.descr.this
        }
    )
    @with_user_context_wrapper('widget_settings_reset')
    async def widget_settings_reset(
        self, 
        mixed_ctx: MixedApplicationContext,
        account: Option(
            int,
            description=Text().get('en').frequent.common.slot,
            description_localizations={
                'ru': Text().get('ru').frequent.common.slot,
                'pl': Text().get('pl').frequent.common.slot,
                'uk': Text().get('ua').frequent.common.slot
            },
            required=False,
            default=None,
            choices=[x.value for x in AccountSlotsEnum]
        )
        ):
        ctx = mixed_ctx.ctx
        m_ctx = mixed_ctx.m_ctx
        
        game_account, slot = m_ctx.game_account, m_ctx.slot      
        await self.pdb.set_widget_settings(slot=slot, member_id=ctx.author.id, settings=WidgetSettings())
        
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.session_widget_settings_reset.info.success,
                colour='green',
                footer=get_formatted_slot_info(
                    slot=slot,
                    text=Text().get(),
                    game_account=game_account,
                    shorted=True,
                    clear_md=True
                )
            )
        )

def setup(bot: commands.Bot):
    bot.add_cog(SessionWidget(bot))