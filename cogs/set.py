import io
import base64

from PIL import Image
from discord import Option, Attachment
from discord.ext import commands
from discord.commands import ApplicationContext

from lib.auth.discord import DiscordOAuth
from lib.api.async_wotb_api import API
from lib.blacklist.blacklist import check_user
from lib.data_classes.db_player import StatsViewSettings
from lib.exceptions.database import VerificationNotFound
from lib.image.utils.resizer import resize_image, ResizeMode
from lib.settings.settings import Config
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.data_classes.db_server import set_server_settings
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.error_handler.common import hook_exceptions, error_handler
from lib.exceptions.api import NeedMoreBattlesError
from lib.logger.logger import get_logger
from lib.locale.locale import Text
from lib.utils.nickname_handler import handle_nickname
from lib.utils.validators import validate

_log = get_logger(__file__, 'CogSetLogger', 'logs/cog_set.log')
_config = Config().get()


class Set(commands.Cog):
    cog_command_error = hook_exceptions(_log)

    def __init__(self, bot) -> None:
        self.discord_oauth = DiscordOAuth()
        self.err_msg = ErrorMSG()
        self.inf_msg = InfoMSG()
        self.sdb = ServersDB()
        self.db = PlayersDB()
        self.api = API()
        self.bot = bot
        
        
    @commands.slash_command(
            guild_only=True,
            description=Text().get('en').cmds.set_lang.descr.this,
            description_localizations={
                'ru': Text().get('ru').cmds.set_lang.descr.this,
                'pl': Text().get('pl').cmds.set_lang.descr.this,
                'uk': Text().get('ua').cmds.set_lang.descr.this
                }
            )
    async def set_lang(self, ctx: ApplicationContext,
            lang: Option(
                str,
                description=Text().get('en').cmds.set_lang.descr.sub_descr.lang_list,
                description_localizations={
                    'ru': Text().get('ru').cmds.set_lang.descr.sub_descr.lang_list,
                    'pl': Text().get('pl').cmds.set_lang.descr.sub_descr.lang_list,
                    'uk': Text().get('ua').cmds.set_lang.descr.sub_descr.lang_list
                },
                choices=_config.default.available_locales,
                required=True
            ),
        ):
        check_user(ctx)
        
        Text().load_from_context(ctx)

        lang = None if lang == 'auto' else lang
        if self.db.set_member_lang(ctx.author.id, lang):
            Text().load_from_context(ctx)
        else:
            await ctx.respond(embed=self.err_msg.set_lang_unregistered())
            return
        
        await ctx.respond(embed=self.inf_msg.set_lang_ok())
        
    @commands.slash_command(
        guild_only=True,
        description=Text().get('en').cmds.set_player.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.set_player.descr.this,
            'pl': Text().get('pl').cmds.set_player.descr.this,
            'uk': Text().get('ua').cmds.set_player.descr.this
            }
        )
    async def set_player(self, ctx: ApplicationContext, 
            nick_or_id: Option(
                str,
                description=Text().get('en').cmds.set_player.descr.sub_descr.nickname,
                description_localizations={
                    'ru': Text().get('ru').cmds.set_player.descr.sub_descr.nickname,
                    'pl': Text().get('pl').cmds.set_player.descr.sub_descr.nickname,
                    'uk': Text().get('ua').cmds.set_player.descr.sub_descr.nickname
                },
                required=True
            ),
            region: Option(
                str,
                description=Text().get('en').cmds.set_player.descr.sub_descr.region,
                description_localizations={
                    'ru': Text().get('ru').cmds.set_player.descr.sub_descr.region,
                    'pl': Text().get('pl').cmds.set_player.descr.sub_descr.region,
                    'uk': Text().get('ua').cmds.set_player.descr.sub_descr.region
                },
                choices=_config.default.available_regions,
                required=True
            )
        ):
        Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()
        
        nickname_type = validate(nick_or_id, 'nickname')
        
        composite_nickname = handle_nickname(nick_or_id, nickname_type)
        
        player = await self.api.check_and_get_player(
            nickname=composite_nickname.nickname,
            region=region,
            game_id=composite_nickname.player_id,
            discord_id=ctx.author.id
            )
        self.db.set_member(player, override=True)
        _log.debug(f'Set player: {ctx.author.id} {nick_or_id} {region}')
        await ctx.respond(embed=self.inf_msg.set_player_ok())

    @commands.slash_command(
        guild_only=True,
        description=Text().get('en').cmds.server_settings.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.server_settings.descr.this,
            'pl': Text().get('pl').cmds.server_settings.descr.this,
            'uk': Text().get('ua').cmds.server_settings.descr.this
            }
        )
    async def server_settings (
            self,
            ctx: ApplicationContext,
            allow_custom_backgrounds: Option(
                bool,
                description=Text().get('en').cmds.server_settings.descr.sub_descr.allow_custom_backgrounds,
                description_localizations={
                    'ru': Text().get('ru').cmds.server_settings.descr.sub_descr.allow_custom_backgrounds,
                    'pl': Text().get('pl').cmds.server_settings.descr.sub_descr.allow_custom_backgrounds,
                    'uk': Text().get('ua').cmds.server_settings.descr.sub_descr.allow_custom_backgrounds
                },
                required=False,
            )
        ):
        Text().load_from_context(ctx)
        check_user(ctx)

        if ctx.author.guild_permissions.administrator:
            settings = self.sdb.get_server_settings(ctx)
            self.sdb.set_server_settings(
                ctx,
                set_server_settings(
                    allow_custom_backgrounds=allow_custom_backgrounds if allow_custom_backgrounds is not None else settings.allow_custom_backgrounds
                )
            )
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    Text().get().cmds.server_settings.info.set_ok,
                )
            )
        else:
            await ctx.respond(embed=self.err_msg.custom(
                Text().get(),
                Text().get().cmds.server_settings.errors.permission_denied
                )
            )

    @commands.slash_command(
        guild_only=True,
        description=Text().get('en').cmds.set_background.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.set_background.descr.this,
            'pl': Text().get('pl').cmds.set_background.descr.this,
            'uk': Text().get('ua').cmds.set_background.descr.this
            }
        )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def set_background(
            self,
            ctx: ApplicationContext,
            image: Option(
                Attachment,
                description=Text().get('en').cmds.set_background.descr.sub_descr.image,
                description_localizations={
                    'ru': Text().get('ru').cmds.set_background.descr.sub_descr.image,
                    'pl': Text().get('pl').cmds.set_background.descr.sub_descr.image,
                    'uk': Text().get('ua').cmds.set_background.descr.sub_descr.image
                    },
                required=True
                ),
            server: Option(
                bool,
                description=Text().get('en').cmds.set_background.descr.sub_descr.server,
                description_localizations={
                    'ru': Text().get('ru').cmds.set_background.descr.sub_descr.server,
                    'pl': Text().get('pl').cmds.set_background.descr.sub_descr.server,
                    'uk': Text().get('ua').cmds.set_background.descr.sub_descr.server
                    },
                required=False
                ),
            resize_mode: Option(
                str, 
                description='Test resize mode',
                required=False,
                default='AUTO',
                choices=['AUTO', 'RESIZE', 'CROP_OR_FILL'],
                )
            ):
        check_user(ctx)

        if not self.db.check_member(ctx.author.id):
            await ctx.respond(
                    embed=self.err_msg.custom(
                        Text().get(),
                        text=Text().get().cmds.set_background.errors.player_not_registred
                    )
                )
            return
        
        Text().load_from_context(ctx)
        image: Attachment = image
        await ctx.defer()

        if image.content_type not in ['image/png', 'image/jpeg']:
            await ctx.respond(
                embed=self.err_msg.custom(
                    Text().get(),
                    text=Text().get().cmds.set_background.errors.file_error
                )
            )
            return
        
        if image.size > 2_097_152:
            await ctx.respond(
                embed=self.err_msg.custom(
                    Text().get(),
                    text=Text().get().cmds.set_background.errors.oversize
                )
            )
            return
        
        if image.width > 2048 or image.height > 2048:
            await ctx.respond(
                embed=self.err_msg.custom(
                    Text().get(),
                    text=Text().get().cmds.set_background.errors.overresolution
                )
            )
            return
        
        if image.width < 256 or image.height < 256:
            await ctx.respond(
                embed=self.err_msg.custom(
                    Text().get(),
                    text=Text().get().cmds.set_background.errors.small_resolution
                )
            )
            return

        if server:
            if ctx.author.guild_permissions.administrator:
                with io.BytesIO() as buffer:
                    await image.save(buffer)
                    pil_image = Image.open(buffer)
                    pil_image = pil_image.convert('RGBA')
                    pil_image = resize_image(pil_image, (700, 1350), mode=getattr(ResizeMode, resize_mode))
                with io.BytesIO() as buffer:
                    pil_image.save(buffer, format='PNG')
                    self.sdb.set_server_image(
                        base64.b64encode(buffer.getvalue()).decode(),
                        ctx
                    )
                    await ctx.respond(
                        embed=self.inf_msg.custom(
                        Text().get(),
                        text=Text().get().cmds.set_background.info.set_background_ok,
                        colour='green'
                        )
                    )
            else:
                await ctx.respond(
                    embed=self.err_msg.custom(
                        Text().get(),
                        text=Text().get().cmds.set_background.errors.permission_denied
                    )
                )
                
            return

        with io.BytesIO() as buffer:
            await image.save(buffer)
            pil_image = Image.open(buffer)
            pil_image = pil_image.convert('RGBA')
            pil_image = resize_image(pil_image, (700, 1350), mode=getattr(ResizeMode, resize_mode))
        with io.BytesIO() as buffer:
            pil_image.save(buffer, format='PNG')
            self.db.set_member_image(
                ctx.author.id,
                base64.b64encode(buffer.getvalue()).decode(),
            )
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    text=Text().get().cmds.set_background.info.set_background_ok,
                    colour='green'
                    )
                )
    
    @commands.slash_command(
        description=Text().get('en').cmds.session_view_settings.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.session_view_settings.descr.this,
            'pl': Text().get('pl').cmds.session_view_settings.descr.this,
            'uk': Text().get('ua').cmds.session_view_settings.descr.this
        }
    )
    async def session_view_settings(
        self, 
        ctx: ApplicationContext,
        slot_1: Option(
            str,
            choices=_config.image.available_stats,
            required=True,
            ),
        slot_2: Option(
            str,
            choices=_config.image.available_stats,
            required=True,
            ),
        slot_3: Option(
            str,
            choices=_config.image.available_stats,
            required=True,
            ),
        slot_4: Option(
            str,
            choices=_config.image.available_stats,
            required=True,
            ),
        ):
        check_user(ctx)
        Text().load_from_context(ctx)
        stats_settings = {
            'slot_1': slot_1,
            'slot_2': slot_2,
            'slot_3': slot_3,
            'slot_4': slot_4
        }
        for slot, value in stats_settings.copy().items():
            if value == 'empty':
                del stats_settings[slot]
                continue
            
        parsed_stats_settings = {}
        for index, key in enumerate(stats_settings.keys()):
            parsed_stats_settings[f'slot_{index + 1}'] = stats_settings[key]
        
        if len(parsed_stats_settings) == 0:
            await ctx.respond(
                embed=self.err_msg.custom(
                    Text().get(),
                    title=Text().get().frequent.info.warning,
                    text=Text().get().cmds.session_view_settings.errors.empty_slots,
                    colour='orange'
                )
            )
            return
                
        self.db.set_stats_settings(ctx.author.id, StatsViewSettings.model_validate({'slots': parsed_stats_settings}))
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.session_view_settings.info.success,
                colour='green'
            )
        )
        
    @commands.slash_command(
        description=Text().get('en').cmds.session_view_settings_reset.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.session_view_settings_reset.descr.this,
            'pl': Text().get('pl').cmds.session_view_settings_reset.descr.this,
            'uk': Text().get('ua').cmds.session_view_settings_reset.descr.this
        }
    )
    async def session_view_settings_reset(self, ctx: ApplicationContext):
        Text().load_from_context(ctx)
        check_user(ctx)
        
        self.db.set_stats_settings(ctx.author.id, StatsViewSettings())
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.session_view_settings_reset.info.success,
                colour='green'
            )
        )

    @commands.slash_command(
        description=Text().get('en').cmds.set_lock.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.set_lock.descr.this,
            'pl': Text().get('pl').cmds.set_lock.descr.this,
            'uk': Text().get('ua').cmds.set_lock.descr.this
            }
        )
    async def set_lock(
        self, 
        ctx: ApplicationContext,
        lock: Option(
            bool,
            description=Text().get('en').cmds.set_lock.descr.sub_descr.lock,
            description_localizations = {
                'ru': Text().get('ru').cmds.set_lock.descr.sub_descr.lock,
                'pl': Text().get('pl').cmds.set_lock.descr.sub_descr.lock,
                'uk': Text().get('ua').cmds.set_lock.descr.sub_descr.lock
            },
            required=True
            )
        ):
        Text().load_from_context(ctx)
        check_user(ctx)
        
        verify_member = self.db.check_member_is_verified(ctx.author.id)
        
        if verify_member:
            self.db.set_member_lock(ctx.author.id, lock)
        else:
            raise VerificationNotFound()
        
        text = Text().get().cmds.set_lock.info
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=text.set_true if lock else text.set_false,
                colour='green'
            )
        )

def setup(bot: commands.Bot):
    bot.add_cog(Set(bot))