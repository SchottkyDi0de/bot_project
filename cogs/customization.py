from discord import Option, File, Cog
import discord
from discord.ext import commands
from discord.commands import ApplicationContext
from webcolors import rgb_to_hex

from lib.api.async_wotb_api import API
from lib.auth.discord import DiscordOAuth
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.data_classes.db_player import AccountSlotsEnum, ImageSettings, UsedCommand
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.error_handler.common import hook_exceptions
from lib.image.session import ImageGenSession
from lib.locale.locale import Text
from lib.logger.logger import get_logger
from lib.blacklist.blacklist import check_user
from lib.image.utils.color_validator import color_validate
from lib.image.settings_represent import SettingsRepresent
from lib.image.utils.b64_img_handler import img_to_base64
from lib.utils.standard_account_validate import standard_account_validate
from lib.utils.string_parser import insert_data
from lib.utils.bool_to_text import bool_handler
from lib.utils.color_converter import get_tuple_from_color
from lib.settings.settings import Config
from lib.image.themes.theme_loader import get_theme
from lib.data_parser.parse_data import get_session_stats
from lib.views.alt_views import StatsPreview
from lib.utils.slot_info import get_formatted_slot_info

_log = get_logger(__file__, 'CogCustomizationLogger', 'logs/cog_customization.log')
_config = Config().get()

class Customization(Cog):
    cog_command_error = hook_exceptions(_log)

    def __init__(self, bot: commands.Bot):
        self.discord_oauth = DiscordOAuth()
        self.err_msg = ErrorMSG()
        self.inf_msg = InfoMSG()
        self.sdb = ServersDB()
        self.db = PlayersDB()
        self.api = API()
        self.bot = bot

    @commands.slash_command(
        description=Text().get('en').cmds.image_settings.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.image_settings.descr.this,
            'pl': Text().get('pl').cmds.image_settings.descr.this,
            'uk': Text().get('ua').cmds.image_settings.descr.this
            }
        )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def image_settings(
        self,
        ctx: ApplicationContext,
        colorize_stats: Option(
            bool,
            required=False,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.colorize_stats,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.colorize_stats,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.colorize_stats,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.colorize_stats
            }
        ),
        glass_effect: Option(
            int,
            required=False,
            min_value=0,
            max_value=15,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.glass_effect,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.glass_effect,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.glass_effect,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.glass_effect
                }
            ),
        stats_blocks_transparency: Option(
            int,
            min_value=0,
            max_value=100,
            required=False,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.stats_blocks_transparency,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.stats_blocks_transparency,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.stats_blocks_transparency,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.stats_blocks_transparency
                }
            ),
        nickname_color: Option(
            str,
            required=False,
            min_length=4,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.nickname_color,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.nickname_color,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.nickname_color,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.nickname_color
                }
            ),
        clan_tag_color: Option(
            str, 
            required=False,
            min_length=4,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.clan_tag_color,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.clan_tag_color,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.clan_tag_color,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.clan_tag_color
                }
            ),
        stats_color: Option(
            str,
            required=False,
            min_length=4,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.stats_color,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.stats_color,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.stats_color,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.stats_color
                }
            ),
        main_text_color: Option(
            str,
            required=False,
            min_length=4,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.main_text_color,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.main_text_color,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.main_text_color,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.main_text_color
                }
            ),
        stats_text_color: Option(
            str,
            required=False,
            min_length=4,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.stats_text_color,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.stats_text_color,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.stats_text_color,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.stats_text_color
                }
            ),
        disable_flag: Option(
            bool,
            required=False,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.disable_flag,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.disable_flag,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.disable_flag,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.disable_flag
                }
            ),
        hide_nickname: Option(
            bool,
            required=False,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.hide_nickname,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.hide_nickname,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.hide_nickname,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.hide_nickname
                }
            ),
        hide_clan_tag: Option(
            bool,
            required=False,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.hide_clan_tag,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.hide_clan_tag,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.hide_clan_tag,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.hide_clan_tag
                }
            ),
        disable_stats_blocks: Option(
            bool,
            required=False,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.disable_stats_blocks,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.disable_stats_blocks,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.disable_stats_blocks,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.disable_stats_blocks
                }
            ),
        disable_rating_stats: Option(
            bool,
            required=False,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.disable_rating_stats,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.disable_rating_stats,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.disable_rating_stats,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.disable_rating_stats
                }
            ),
        disable_cache_label: Option(
            bool,
            required=False,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.disable_cache_label,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.disable_cache_label,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.disable_cache_label,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.disable_cache_label
                }
            ),
        positive_stats_color: Option(
            str,
            required=False,
            min_length=4,
            description=Text().get('en').cmds.image_settings_get.items.positive_stats_color,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings_get.items.positive_stats_color,
                'pl': Text().get('pl').cmds.image_settings_get.items.positive_stats_color,
                'uk': Text().get('ua').cmds.image_settings_get.items.positive_stats_color
                }
            ),
        negative_stats_color: Option(
            str,
            required=False,
            min_length=4,
            description=Text().get('en').cmds.image_settings_get.items.negative_stats_color,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings_get.items.negative_stats_color,
                'pl': Text().get('pl').cmds.image_settings_get.items.negative_stats_color,
                'uk': Text().get('ua').cmds.image_settings_get.items.negative_stats_color
                }
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
        await Text().load_from_context(ctx)

        game_account, member, slot = await standard_account_validate(account_id=ctx.author.id, slot=account)
        await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
        await ctx.defer()

        image_settings = await self.db.get_image_settings(slot=slot, member=member)
        color_error_data = []
        color_error = False
        
        current_settings = {
            'theme': 'custom',
            'colorize_stats': colorize_stats,
            'glass_effect': glass_effect,
            'main_text_color': main_text_color,
            'stats_blocks_transparency': stats_blocks_transparency,
            'nickname_color': nickname_color,
            'clan_tag_color': clan_tag_color,
            'stats_color': stats_color,
            'stats_text_color': stats_text_color,
            'disable_flag': disable_flag,
            'hide_nickname': hide_nickname,
            'hide_clan_tag': hide_clan_tag,
            'disable_stats_blocks': disable_stats_blocks,
            'disable_rating_stats': disable_rating_stats,
            'disable_cache_label': disable_cache_label,
            'positive_stats_color': positive_stats_color,
            'negative_stats_color': negative_stats_color
        }
        
        set_values_count = 0
        for key, value in current_settings.items():
            if value is None:
                current_settings[key] = getattr(image_settings, key)
                continue
            elif '_color' in key:
                set_values_count += 1
                validate_result = color_validate(value)
                if validate_result is None:
                    color_error = True
                    color_error_data.append({'param_name': key, 'value': value})
                    current_settings[key] = getattr(image_settings, key)
                elif validate_result[1] == "hex":
                    current_settings[key] = value
                elif validate_result[1] == "rgb":
                    current_settings[key] = rgb_to_hex(get_tuple_from_color(value))
            elif key == 'stats_blocks_transparency':
                set_values_count += 1
                current_settings[key] = value / 100
            else:
                set_values_count += 1
                current_settings[key] = value
                    
        if set_values_count == 0:
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    text=Text().get().cmds.image_settings.errors.changes_not_found,
                    title=Text().get().frequent.info.warning,
                    colour='orange'
                )
            )
            return
        
        if color_error:
            text = ''
            for i in color_error_data:
                text += insert_data(
                    Text().get().cmds.image_settings.errors.color_error,
                    {
                        'param_name': i['param_name'],
                        'value': i['value']
                    }
                ) + '\n'
                
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    text=text + Text().get().cmds.image_settings.items.color_error_note,
                    title=Text().get().frequent.info.warning,
                    footer=Text().get().cmds.image_settings.items.color_error_footer,
                    colour='orange',
                ).add_field(name='Color picker', value='[Click here](https://g.co/kgs/FwKjhNE)', inline=False)
            )
            await self.db.set_image_settings(
                slot=slot,
                member_id=member.id, 
                settings=ImageSettings.model_validate(current_settings)
            )
            return

        current_image_settings = ImageSettings.model_validate(current_settings)
        
        data = await self.api.get_stats(region=game_account.region, game_id=game_account.game_id)
        diff_data = get_session_stats(data, data, zero_bypass=True)
        
        image = ImageGenSession().generate(
            data=data, 
            diff_data=diff_data, 
            player=member, 
            server=self.sdb.get_server(ctx), 
            slot=slot,
            force_image_settings=current_image_settings
        )
        
        img_file = File(image, 'session.png')
        image.close()
        
        view = StatsPreview(
            player_id=member.id,
            slot=slot,
            text=Text().get(),
            image_settings=current_image_settings
        ).get_view()
        
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.image_settings.info.preview
            ),
            file=img_file,
            view=view
        )

    @commands.slash_command(
        guild_only=True, 
        description=Text().get('en').cmds.image_settings_get.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.image_settings_get.descr.this,
            'pl': Text().get('pl').cmds.image_settings_get.descr.this,
            'uk': Text().get('ua').cmds.image_settings_get.descr.this
            }
        )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def image_settings_get(
        self, 
        ctx: discord.commands.ApplicationContext,
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
        await Text().load_from_context(ctx)
        await ctx.defer()

        game_account, member, slot = await standard_account_validate(account_id=ctx.author.id, slot=account)
        await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
        image_bytes = SettingsRepresent().draw(game_account.image_settings)
        file = File(image_bytes, 'image_settings.png')
        
        embed = self.inf_msg.custom(
            Text().get(),
            text=Text().get().cmds.image_settings_get.info.get_ok,
            footer=get_formatted_slot_info(
                slot=slot,
                text=Text().get(),
                game_account=game_account,
                shorted=True,
                clear_md=True
            )
        )
        
        await ctx.respond(embed=embed, file=file)
            
    @commands.slash_command(
        guild_only=True,
        description=Text().get('en').cmds.image_settings_reset.descr.this,
        description_localizations = {
            'ru': Text().get('ru').cmds.image_settings_reset.descr.this,
            'pl': Text().get('pl').cmds.image_settings_reset.descr.this,
            'uk': Text().get('ua').cmds.image_settings_reset.descr.this
            }
        )
    async def image_settings_reset(
        self, 
        ctx: ApplicationContext,
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
        await Text().load_from_context(ctx)
        check_user(ctx)

        game_account, member, slot = await standard_account_validate(slot=account, account_id=ctx.author.id)
        await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
        await self.db.set_image_settings(slot=slot, member_id=member.id, settings=ImageSettings())
    
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                Text().get().cmds.image_settings_reset.info.reset_ok,
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
        guild_only=True,
        description=Text().get('en').cmds.server_settings_get.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.server_settings_get.descr.this,
            'pl': Text().get('pl').cmds.server_settings_get.descr.this,
            'uk': Text().get('ua').cmds.server_settings_get.descr.this
        }
    )
    async def server_settings_get(self, ctx: ApplicationContext):
        check_user(ctx)

        await Text().load_from_context(ctx)
        member = await self.db.check_member_exists(member_id=ctx.author.id, raise_error=False, get_if_exist=True)
        if not isinstance(member, bool):
            await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
            
        server_settings = self.sdb.get_server_settings(ctx)
        embed = self.inf_msg.custom(
            Text().get(),
            title=Text().get().cmds.server_settings_get.info.get_ok,
            text=insert_data(
                Text().get().cmds.server_settings_get.items.settings_list,
                {
                    'allow_custom_backgrounds': bool_handler(server_settings.allow_custom_backgrounds)
                }
            ),
        )
        await ctx.respond(embed=embed)
            
    @commands.slash_command(
        description=Text().get('en').cmds.reset_background.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.reset_background.descr.this,
            'pl': Text().get('pl').cmds.reset_background.descr.this,
            'uk': Text().get('ua').cmds.reset_background.descr.this
        }
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def unset_background(
        self,
        ctx: ApplicationContext,
        server: Option(
            bool,
            description=Text().get('en').cmds.reset_background.descr.sub_descr.server,
            description_localizations={
                'ru': Text().get('ru').cmds.reset_background.descr.sub_descr.server,
                'pl': Text().get('pl').cmds.reset_background.descr.sub_descr.server,
                'uk': Text().get('ua').cmds.reset_background.descr.sub_descr.server
            },
            required=False,
            default=False
            )
        ):
        await Text().load_from_context(ctx)
        check_user(ctx)
        
        if server:
            if ctx.author.guild_permissions.administrator:
                self.sdb.del_server_image(ctx.guild.id)
                await ctx.respond(
                    embed=self.inf_msg.custom(
                        Text().get(),
                        text=Text().get().cmds.reset_background.info.unset_background_ok,
                        colour='green'
                    )
                )
            else:
                await ctx.respond(
                    embed=self.err_msg.custom(
                        Text().get(),
                        text=Text().get().cmds.reset_background.errors.permission_denied
                    )
                )
            return
        
        _, member, _ = await standard_account_validate(slot=None, account_id=ctx.author.id)
        await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
                
        await self.db.set_image(member_id=member.id, image=None)
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.reset_background.info.unset_background_ok,
                colour='green'
            )
        )

def setup(bot: commands.Bot):
    bot.add_cog(Customization(bot))
