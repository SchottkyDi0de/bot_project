from datetime import timedelta
import io

from PIL import Image
from discord import Interaction, Option, Attachment, SelectOption
from discord import ui, ButtonStyle
from discord.ext import commands
from discord.commands import ApplicationContext

from lib.api.async_wotb_api import API
from lib.utils.slot_info import get_formatted_slot_info
from lib.utils.standard_account_validate import standard_account_validate
from lib.utils.string_parser import insert_data
from lib.views.alt_views import DeleteAccountConfirmation, StartSession, SlotOverride, SwitchAccount
from lib.blacklist.blacklist import check_user
from lib.data_classes.db_player import StatsViewSettings, AccountSlotsEnum, UsedCommand
from lib.exceptions.database import VerificationNotFound
from lib.image.utils.resizer import resize_image, ResizeMode
from lib.settings.settings import Config
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.data_classes.db_server import set_server_settings
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.error_handler.common import hook_exceptions
from lib.logger.logger import get_logger
from lib.locale.locale import Text
from lib.utils.nickname_handler import handle_nickname
from lib.utils.validators import validate
from lib.image.themes.theme_loader import get_theme
from lib.data_classes.db_player import ImageSettings
from lib.data_classes.themes import Theme
from lib.image.utils.b64_img_handler import img_to_base64, attachment_to_img

_log = get_logger(__file__, 'CogSetLogger', 'logs/cog_set.log')
_config = Config().get()


class Set(commands.Cog):
    cog_command_error = hook_exceptions(_log)

    def __init__(self, bot) -> None:
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
        await Text().load_from_context(ctx)
        await self.db.check_member_exists(ctx.author.id)
        check_user(ctx)
        
        await Text().load_from_context(ctx)

        lang = None if lang == 'auto' else lang
        await self.db.set_lang(ctx.author.id, lang)
        
        if lang is None:
            await Text().load_from_context(ctx)
        else:
            Text().load(lang)
            
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
    async def set_player(self,
            ctx: ApplicationContext, 
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
            ),
            slot: Option(
                int,
                description=Text().get('en').frequent.common.slot,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.slot,
                    'pl': Text().get('pl').frequent.common.slot,
                    'uk': Text().get('ua').frequent.common.slot
                },
                choices=[x.value for x in AccountSlotsEnum],
                required=True,
            )
        ):
        await Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()
        
        slot = AccountSlotsEnum(int(slot))
        nickname_type = validate(nick_or_id, 'nickname')
        composite_nickname = handle_nickname(nick_or_id, nickname_type)
        
        game_account = await self.api.check_and_get_player(
            nickname=composite_nickname.nickname,
            region=region,
            game_id=composite_nickname.player_id,
            discord_id=ctx.author.id
        )
        member = await self.db.check_member_exists(member_id=ctx.author.id, raise_error=False, get_if_exist=True)
        if not isinstance(member, bool):
            await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
            if not await self.db.check_slot_empty(slot, member=member, raise_error=False):
                view = SlotOverride(Text().get(), game_account, ctx.author.id, slot)
                await ctx.respond(
                    embed=self.inf_msg.custom(
                        Text().get(),
                        text=insert_data(
                            Text().get().cmds.set_player.info.slot_override,
                            {'slot_data': get_formatted_slot_info(
                                slot, 
                                Text().get(), 
                                await self.db.get_game_account(slot=slot, member=member)
                                )
                            }
                        ),
                        colour='orange'
                    ),
                    view=view.get_view()
                )
                return
        
        await self.db.set_member(slot=AccountSlotsEnum(slot), member_id=ctx.author.id, game_account=game_account, slot_override=True)
        view = StartSession(Text().get(), ctx.author.id, slot, game_account)
        _log.info(f'Set player: {ctx.author.id} {nick_or_id} {region} | slot: {AccountSlotsEnum(slot).name}')
        await ctx.respond(
            embed=self.inf_msg.set_player_ok(),
            view=view.get_view()
        )
        
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
        await Text().load_from_context(ctx)
        check_user(ctx)
        
        member = await self.db.check_member_exists(member_id=ctx.author.id, raise_error=False, get_if_exist=True)
        if not isinstance(member, bool):
            await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)

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
                description=Text().get('en').cmds.set_background.descr.sub_descr.resize_mode,
                description_localizations={
                    'ru': Text().get('ru').cmds.set_background.descr.sub_descr.resize_mode,
                    'pl': Text().get('pl').cmds.set_background.descr.sub_descr.resize_mode,
                    'uk': Text().get('ua').cmds.set_background.descr.sub_descr.resize_mode
                },
                required=False,
                default=ResizeMode.AUTO.name,
                choices=[x.name for x in ResizeMode],
                )
            ):
        check_user(ctx)
        await Text().load_from_context(ctx)
        
        member = await self.db.check_member_exists(member_id=ctx.author.id, raise_error=False, get_if_exist=True)

        if not isinstance(member, bool):
            await ctx.respond(
                embed=self.err_msg.custom(
                    Text().get(),
                    text=Text().get().cmds.set_background.errors.player_not_registred
                )
            )
            return
        
        await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
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
                pil_image = attachment_to_img(await image.read())
                pil_image = resize_image(pil_image.convert('RGBA'), (800, 1350), mode=ResizeMode[resize_mode])
                
                base64_img = img_to_base64(pil_image)
                self.sdb.set_server_image(
                    base64_img,
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

        pil_image = attachment_to_img(await image.read())
        pil_image = resize_image(pil_image.convert('RGBA'), (800, 1350), mode=ResizeMode[resize_mode])
        
        base64_img = img_to_base64(pil_image)
        await self.db.set_image(ctx.author.id, base64_img)
        
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
    async def stats_position(
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
            ),
        ):
        await Text().load_from_context(ctx)
        stats_settings = {
            'slot_1': slot_1,
            'slot_2': slot_2,
            'slot_3': slot_3,
            'slot_4': slot_4
        }
        game_account, member, account_slot = await standard_account_validate(account_id=ctx.user.id, slot=account)
        await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
        stats_view_settings = game_account.stats_view_settings
        
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
                
        await self.db.set_stats_view_settings(
            slot=account_slot,
            member_id=member.id,
            settings=StatsViewSettings.model_validate(
                {'common_slots': parsed_stats_settings, 'rating_slots': stats_view_settings.rating_slots}
                )
            )
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.session_view_settings.info.success,
                colour='green',
                footer=get_formatted_slot_info(
                    slot=account_slot,
                    text=Text().get(),
                    game_account=await self.db.get_game_account(slot=account_slot, member_id=member.id),
                    shorted=True,
                    clear_md=True
                )
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
    async def stats_position_rating(
        self, 
        ctx: ApplicationContext,
        slot_1: Option(
            str,
            choices=_config.image.available_rating_stats,
            required=True,
            ),
        slot_2: Option(
            str,
            choices=_config.image.available_rating_stats,
            required=True,
            ),
        slot_3: Option(
            str,
            choices=_config.image.available_rating_stats,
            required=True,
            ),
        slot_4: Option(
            str,
            choices=_config.image.available_rating_stats,
            required=True,
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
            required=False,
            default=None
            ),
        ):
        await Text().load_from_context(ctx)
        
        game_account, member, account_slot = await standard_account_validate(ctx.user.id, account)
        await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
        stats_view_settings = game_account.stats_view_settings
        
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
                    colour='orange',
                    footer=get_formatted_slot_info(
                        slot=account,
                        text=Text().get(),
                        game_account=await self.db.get_game_account(slot=account, member_id=ctx.user.id),
                        shorted=True,
                        clear_md=True
                    )
                )
            )
            return
                
        await self.db.set_stats_view_settings(
            slot=account_slot,
            member_id=member.id,
            settings=StatsViewSettings.model_validate(
                {'rating_slots': parsed_stats_settings, 'common_slots': stats_view_settings.common_slots}
            ),
        ),
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.session_view_settings.info.success,
                colour='green',
                footer=get_formatted_slot_info(
                    slot=account,
                    text=Text().get(),
                    game_account=await self.db.get_game_account(slot=account_slot, member_id=member.id),
                    shorted=True,
                    clear_md=True
                )
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
    async def stats_position_reset(
        self, 
        ctx: ApplicationContext,
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
            ),
        ):
        await Text().load_from_context(ctx)
        check_user(ctx)
        
        _, member, account_slot = await standard_account_validate(ctx.user.id, account)
        await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
        
        await self.db.set_stats_view_settings(slot=account_slot, member_id=member.id, settings=StatsViewSettings())
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.session_view_settings_reset.info.success,
                colour='green',
                footer=get_formatted_slot_info(
                    slot=account,
                    text=Text().get(),
                    game_account=await self.db.get_game_account(slot=account_slot, member_id=member.id),
                    shorted=True,
                    clear_md=True
                )
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
            required=False,
            default=None
            ),
        ):
        await Text().load_from_context(ctx)
        check_user(ctx)
        
        _, member, account_slot = await standard_account_validate(ctx.user.id, account, check_verified=True)
        await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
        await self.db.set_member_lock(slot=account_slot, member_id=member.id, lock=lock)
        
        
        text = Text().get().cmds.set_lock.info
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=text.set_true if lock else text.set_false,
                colour='green',
                footer=get_formatted_slot_info(
                    slot=account,
                    text=Text().get(),
                    game_account=await self.db.get_game_account(slot=account_slot, member_id=member.id),
                    shorted=True,
                    clear_md=True
                )
            )
        )
    
    @commands.slash_command(
        description=Text().get('en').cmds.set_theme.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.set_theme.descr.this,
            'pl': Text().get('pl').cmds.set_theme.descr.this,
            'uk': Text().get('ua').cmds.set_theme.descr.this
        }
    )
    async def set_theme(
        self, 
        ctx: ApplicationContext,
        theme: Option(
            str,
            description=Text().get('en').cmds.set_theme.items.theme,
            description_localizations={
                'ru': Text().get('ru').cmds.set_theme.items.theme,
                'pl': Text().get('pl').cmds.set_theme.items.theme,
                'uk': Text().get('ua').cmds.set_theme.items.theme
            },
            choices=_config.themes.available
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
            required=False,
            default=None
            ),
        ):
        await Text().load_from_context(ctx)
        check_user(ctx)
        
        theme: Theme = get_theme(theme)
        game_account, member, slot = await standard_account_validate(ctx.user.id, account)
        await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
        await self.db.set_image_settings(
            slot=slot, member_id=member.id, settings=theme.image_settings
        )
        await self.db.set_image(member_id=member.id, image=img_to_base64(theme.bg))
        
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.set_theme.info.success,
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
        description=Text().get('en').cmds.delete_player.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.delete_player.descr.this,
            'pl': Text().get('pl').cmds.delete_player.descr.this,
            'uk': Text().get('ua').cmds.delete_player.descr.this
        }
    )
    async def delete_player(self, ctx: ApplicationContext):
        await Text().load_from_context(ctx)
        check_user(ctx)
        
        await self.db.check_member_exists(ctx.author.id)
        
        view = DeleteAccountConfirmation(Text().get(), ctx.author.id).get_view()
        await ctx.respond(
            embed=self.inf_msg.custom(
                Text().get(),
                text=Text().get().cmds.delete_player.info.warn,
                colour='red'
            ),
            view=view
        )
    
    @commands.slash_command(
        description=Text().get('en').cmds.switch_account.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.switch_account.descr.this,
            'pl': Text().get('pl').cmds.switch_account.descr.this,
            'uk': Text().get('ua').cmds.switch_account.descr.this
        }
    )
    async def switch_account(self, ctx: ApplicationContext):
        await Text().load_from_context(ctx)
        
        game_account, member, slot = await standard_account_validate(account_id=ctx.user.id, slot=None)
        available_slots = await self.db.get_all_used_slots(member=member)
        await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
        
        if len(available_slots) == 1:
            await ctx.respond(
                embed=self.inf_msg.custom(
                    Text().get(),
                    text=Text().get().cmds.switch_account.errors.no_slots_for_select,
                    colour='orange'
                )
            )
            return
        
        available_slots.remove(slot)
        choices: list[SelectOption] = []
        for expected_slot in available_slots:
            choices.append(
                SelectOption(
                label=get_formatted_slot_info(
                    expected_slot, 
                    text=Text().get(),
                    game_account=await PlayersDB().get_game_account(slot=expected_slot, member=member),
                    shorted=True,
                    clear_md=True
                    ),
                value=expected_slot.name
                )
            )
        
        embed = self.inf_msg.custom(
            Text().get(),
            title='',
            text=get_formatted_slot_info(
                slot=slot,
                text=Text().get(),
                game_account=game_account,
            ),
            colour='orange'
        )
        view = SwitchAccount(text=Text().get(), member=member, choices=choices, slot=slot).get_view()
        
        await ctx.respond(view=view, embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Set(bot))