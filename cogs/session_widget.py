from discord.ui import View, Button
from discord.ext import commands
from discord.commands import ApplicationContext, Option

from lib.blacklist.blacklist import check_user
from lib.data_classes.db_player import WidgetSettings
from lib.database.players import PlayersDB
from lib.embeds.info import InfoMSG
from lib.error_handler.common import hook_exceptions
from lib.locale.locale import Text
from lib.logger.logger import get_logger
from lib.settings.settings import Config
from lib.utils.string_parser import insert_data
from lib.exceptions.database import MemberNotFound, LastStatsNotFound

_config = Config().get()
_log = get_logger(__file__, 'SessionWidgetLogger', 'logs/session_widget.log')

class SessionWidget(commands.Cog):
    cog_command_error = hook_exceptions(_log)
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pdb = PlayersDB()
        self.inf_msg = InfoMSG()
        
    @commands.slash_command(
        description=Text().get('en').cmds.session_widget.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.session_widget.descr.this,
            'pl': Text().get('pl').cmds.session_widget.descr.this,
            'uk': Text().get('ua').cmds.session_widget.descr.this
        }
    )
    async def session_widget(self, ctx: ApplicationContext):
        Text().load_from_context(ctx)
        check_user(ctx)
        
        if not self.pdb.check_member(ctx.author.id):
            raise MemberNotFound
        
        if not self.pdb.check_member_last_stats(ctx.author.id):
            raise LastStatsNotFound
        
        _log.debug(f'Sending session widget to {ctx.author.id}')
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.session_widget.info.success,
                colour='green'
            ),
            view=View(
                Button(
                    label = Text().get().cmds.session_widget.items.btn,
                    url = insert_data(
                        _config.session_widget.url,
                        {
                            'host' : _config.server.host,
                            'port' : _config.server.port,
                            'user_id' : ctx.author.id
                        }
                    )
                )
            ),
            ephemeral=True
        )
    
    @commands.slash_command(
        description=Text().get('en').cmds.session_widget_settings.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.session_widget_settings.descr.this,
            'pl': Text().get('pl').cmds.session_widget_settings.descr.this,
            'uk': Text().get('ua').cmds.session_widget_settings.descr.this
        }
    )
    async def session_widget_settings(
            self, 
            ctx: ApplicationContext,
            disable_bg = Option(
                bool,
                description=Text().get('en').cmds.session_widget_settings.items.disable_bg,
                description_localizations={
                    'ru': Text().get('ru').cmds.session_widget_settings.items.disable_bg,
                    'pl': Text().get('pl').cmds.session_widget_settings.items.disable_bg,
                    'uk': Text().get('ua').cmds.session_widget_settings.items.disable_bg
                    },
                default = None
                ),
            disable_nickname = Option(
                bool,
                description=Text().get('en').cmds.session_widget_settings.items.disable_nickname,
                description_localizations={
                    'ru': Text().get('ru').cmds.session_widget_settings.items.disable_nickname,
                    'pl': Text().get('pl').cmds.session_widget_settings.items.disable_nickname,
                    'uk': Text().get('ua').cmds.session_widget_settings.items.disable_nickname
                },
                default = None
            ),
            max_stats_blocks=Option(
                int,
                description=Text().get('en').cmds.session_widget_settings.items.max_stats_blocks,
                description_localizations={
                    'ru': Text().get('ru').cmds.session_widget_settings.items.max_stats_blocks,
                    'pl': Text().get('pl').cmds.session_widget_settings.items.max_stats_blocks,
                    'uk': Text().get('ua').cmds.session_widget_settings.items.max_stats_blocks
                },
                min_value=1,
                max_value=4,
                default=None
            ),
            max_stats_small_blocks = Option(
                int,
                description=Text().get('en').cmds.session_widget_settings.items.max_stats_small_blocks,
                description_localizations={
                    'ru': Text().get('ru').cmds.session_widget_settings.items.max_stats_small_blocks,
                    'pl': Text().get('pl').cmds.session_widget_settings.items.max_stats_small_blocks,
                    'uk': Text().get('ua').cmds.session_widget_settings.items.max_stats_small_blocks
                },
                min_value=0,
                max_value=2,
                default=None
            ),
            update_per_seconds = Option(
                int,
                description=Text().get('en').cmds.session_widget_settings.items.update_per_seconds,
                description_localizations={
                    'ru': Text().get('ru').cmds.session_widget_settings.items.update_per_seconds,
                    'pl': Text().get('pl').cmds.session_widget_settings.items.update_per_seconds,
                    'uk': Text().get('ua').cmds.session_widget_settings.items.update_per_seconds
                },
                min_value=60,
                max_value=360,
                default=None
            ),
            stats_blocks_transparency = Option(
                float,
                description=Text().get('en').cmds.session_widget_settings.items.stats_blocks_transparency,
                description_localizations={
                    'ru': Text().get('ru').cmds.session_widget_settings.items.stats_blocks_transparency,
                    'pl': Text().get('pl').cmds.session_widget_settings.items.stats_blocks_transparency,
                    'uk': Text().get('ua').cmds.session_widget_settings.items.stats_blocks_transparency
                },
                min_value=0,
                max_value=1,
                default=None
            ),
            disable_main_stats_block = Option(
                bool,
                description=Text().get('en').cmds.session_widget_settings.items.disable_main_stats_block,
                description_localizations={
                    'ru': Text().get('ru').cmds.session_widget_settings.items.disable_main_stats_block,
                    'pl': Text().get('pl').cmds.session_widget_settings.items.disable_main_stats_block,
                    'uk': Text().get('ua').cmds.session_widget_settings.items.disable_main_stats_block
                },
                default=None
            ),
            use_bg_for_stats_blocks = Option(
                bool,
                description=Text().get('en').cmds.session_widget_settings.items.use_bg_for_stats_blocks,
                description_localizations={
                    'ru': Text().get('ru').cmds.session_widget_settings.items.use_bg_for_stats_blocks,
                    'pl': Text().get('pl').cmds.session_widget_settings.items.use_bg_for_stats_blocks,
                    'uk': Text().get('ua').cmds.session_widget_settings.items.use_bg_for_stats_blocks
                },
                default=None
            ),
            adaptive_width = Option(
                bool,
                description=Text().get('en').cmds.session_widget_settings.items.adaptive_width,
                description_localizations={
                    'ru': Text().get('ru').cmds.session_widget_settings.items.adaptive_width,
                    'pl': Text().get('pl').cmds.session_widget_settings.items.adaptive_width,
                    'uk': Text().get('ua').cmds.session_widget_settings.items.adaptive_width
                },
                default=None
            ),
            stats_block_color = Option(
                str,
                description=Text().get('en').cmds.session_widget_settings.items.stats_block_color,
                description_localizations={
                    'ru': Text().get('ru').cmds.session_widget_settings.items.stats_block_color,
                    'pl': Text().get('pl').cmds.session_widget_settings.items.stats_block_color,
                    'uk': Text().get('ua').cmds.session_widget_settings.items.stats_block_color
                },
                default=None
            )
        ):
        Text().load_from_context(ctx)
        check_user(ctx)
        
        widget_settings = self.pdb.get_member_widget_settings(ctx.author.id)
        
        current_settings = {
            'adaptive_width': adaptive_width,
            'stats_block_color': stats_block_color,
            'use_bg_for_stats_blocks': use_bg_for_stats_blocks,
            'disable_main_stats_block': disable_main_stats_block,
            'stats_blocks_transparency': stats_blocks_transparency,
            'update_per_seconds': update_per_seconds,
            'max_stats_small_blocks': max_stats_small_blocks,
            'max_stats_blocks': max_stats_blocks,
            'disable_nickname': disable_nickname,
            'disable_bg': disable_bg
        }
        
        set_values_count = 0
        for key, value in current_settings.items():
            if value is None:
                current_settings[key] = getattr(widget_settings, key)
                continue
            else:
                set_values_count += 1
        
        if set_values_count == 0:
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    text=Text().get().cmds.session_widget_settings.errors.nothing_changed,
                    colour='orange'
                )
            )
            return
        
        self.pdb.set_member_widget_settings(ctx.author.id, WidgetSettings.model_validate(current_settings))
        
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.session_widget_settings.info.success,
                colour='green'
            )
        )
    
    async def session_widget_settings_reset(self, ctx: ApplicationContext):
        Text().load_from_context(ctx)
        check_user(ctx)
        
        self.pdb.set_member_widget_settings(ctx.author.id, WidgetSettings())
        
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.session_widget_settings_reset.info.success,
                colour='green'
            )
        )

def setup(bot: commands.Bot):
    bot.add_cog(SessionWidget(bot))