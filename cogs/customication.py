import traceback

from discord import Option, File, Cog
from discord.ext import commands

from lib.api.async_wotb_api import API
from lib.auth.discord import DiscordOAuth
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.data_classes.db_player import ImageSettings
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.exceptions.blacklist import UserBanned
from lib.locale.locale import Text
from lib.logger.logger import get_logger
from lib.blacklist.blacklist import check_user
from lib.image.utils.hex_color_validator import hex_color_validate
from lib.image.settings_represent import SettingsRepresent
from lib.utils.string_parser import insert_data
from lib.utils.bool_to_text import bool_handler
from lib.utils.views import ViewMeta
from lib.utils.stats_preview import StatsPreview

_log = get_logger(__file__, 'CogCustomizationLogger', 'logs/cog_customization.log')


class Customization(Cog):
    def __init__(self, bot):
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
        ctx: commands.Context,
        use_custom_bg: Option(
            bool,
            required=False,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.use_custom_bg,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.use_custom_bg,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.use_custom_bg,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.use_custom_bg
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
        blocks_bg_opacity: Option(
            int,
            min_value=0,
            max_value=100,
            required=False,
            description=Text().get('en').cmds.image_settings.descr.sub_descr.blocks_bg_brightness,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings.descr.sub_descr.blocks_bg_brightness,
                'pl': Text().get('pl').cmds.image_settings.descr.sub_descr.blocks_bg_brightness,
                'uk': Text().get('ua').cmds.image_settings.descr.sub_descr.blocks_bg_brightness
                }
            ),
        nickname_color: Option(
            str,
            required=False,
            min_length=4,
            max_length=7,
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
            max_length=7,
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
            max_length=7,
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
            max_length=7,
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
            max_length=7,  
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
            max_length=7,
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
            max_length=7,
            description=Text().get('en').cmds.image_settings_get.items.negative_stats_color,
            description_localizations={
                'ru': Text().get('ru').cmds.image_settings_get.items.negative_stats_color,
                'pl': Text().get('pl').cmds.image_settings_get.items.negative_stats_color,
                'uk': Text().get('ua').cmds.image_settings_get.items.negative_stats_color
                }
            )
        ):
        Text().load_from_context(ctx)
        check_user(ctx)

        if not self.db.check_member(ctx.author.id):
            await ctx.respond(embed=self.inf_msg.player_not_registred())
            return

        image_settings = self.db.get_image_settings(ctx.author.id)
        color_error_data = []
        color_error = False
        
        current_settings = {
            'use_custom_bg': use_custom_bg,
            'glass_effect': glass_effect,
            'main_text_color': main_text_color,
            'blocks_bg_opacity': blocks_bg_opacity,
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
            else:
                set_values_count += 1
            if 'color' in key:
                set_values_count += 1
                if not hex_color_validate(value):
                    color_error = True
                    color_error_data.append({'param_name': key, 'value': value})
                    current_settings[key] = getattr(image_settings, key)
            if key == 'blocks_bg_opacity':
                set_values_count += 1
                current_settings[key] = value / 100
                    
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
            self.db.set_image_settings(ctx.author.id, ImageSettings.model_validate(current_settings))
            return
            

        currecnt_image_settings = ImageSettings.model_validate(current_settings)
        sptext, spimage = StatsPreview().preview(ctx, currecnt_image_settings)
        await ctx.respond(sptext, file=spimage, 
                          view=ViewMeta(ctx, 'image_settings', None, currecnt_image_settings))

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
    async def image_settings_get(self, ctx: commands.Context):
        Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()

        if not self.db.check_member(ctx.author.id):
            await ctx.respond(embed=self.inf_msg.player_not_registred())
            return
        
        image_settings = self.db.get_image_settings(ctx.author.id)
        embed = self.inf_msg.custom(
            Text().get(),
            text=Text().get().cmds.image_settings_get.info.get_ok,
        )
        image = File(SettingsRepresent().draw(image_settings), filename='img_settings.png')
        await ctx.respond(embed=embed)
        await ctx.channel.send(file=image)
            
    @commands.slash_command(
        guild_only=True,
        description=Text().get('en').cmds.image_settings_reset.descr.this,
        description_localizations = {
            'ru': Text().get('ru').cmds.image_settings_reset.descr.this,
            'pl': Text().get('pl').cmds.image_settings_reset.descr.this,
            'uk': Text().get('ua').cmds.image_settings_reset.descr.this
            }
        )
    async def image_settings_reset(self, ctx: commands.Context):
        Text().load_from_context(ctx)
        check_user(ctx)

        if not self.db.check_member(ctx.author.id):
            await ctx.respond(embed=self.inf_msg.player_not_registred())
            return
        
        self.db.set_image_settings(ctx.author.id, ImageSettings.model_validate({}))
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                Text().get().cmds.image_settings_reset.info.reset_ok
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
    async def server_settings_get(self, ctx: commands.Context):
        check_user(ctx)

        Text().load_from_context(ctx)
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
        ctx: commands.Context,
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
        Text().load_from_context(ctx)
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
        elif self.db.check_member(ctx.author.id):
            self.db.del_member_image(ctx.author.id)
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
                    text=Text().get().cmds.set_background.errors.player_not_registred
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
    bot.add_cog(Customization(bot))
