import io
import base64
import traceback

from PIL import Image
from discord import Option, Attachment
from discord.ext import commands

from lib.image.utils.resizer import resize_image
from lib.settings.settings import Config
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.locale.locale import Text
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.blacklist.blacklist import check_user
from lib.exceptions.blacklist import UserBanned
from lib.logger.logger import get_logger
from lib.api.async_wotb_api import API
from lib.exceptions import api
from lib.auth.dicord import DiscordOAuth

_log = get_logger(__name__, 'CogSetLogger', 'logs/cog_set.log')
_config = Config().get()


class Set(commands.Cog):
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
            description=Text().get().cmds.set_lang.descr.this,
            description_localizations={
                'ru': Text().get('ru').cmds.set_lang.descr.this,
                'pl': Text().get('pl').cmds.set_lang.descr.this,
                'uk': Text().get('ua').cmds.set_lang.descr.this
                }
            )
    async def set_lang(self, ctx: commands.Context,
            lang: Option(
                str,
                description=Text().get().cmds.set_lang.descr.sub_descr.lang_list,
                description_localizations={
                    'ru': Text().get('ru').cmds.set_lang.descr.sub_descr.lang_list,
                    'pl': Text().get('pl').cmds.set_lang.descr.sub_descr.lang_list,
                    'uk': Text().get('ua').cmds.set_lang.descr.sub_descr.lang_list
                },
                choices=_config.default.available_locales,
                required=True
            ),
        ):


        try:
            check_user(ctx)
        except UserBanned:
            return
        
        try:
            Text().load_from_context(ctx)
            lang = None if lang == 'auto' else lang
            if self.db.set_member_lang(ctx.author.id, lang):
                Text().load_from_context(ctx)
            else:
                await ctx.respond(embed=self.err_msg.set_lang_unregistred())
                return
            
            await ctx.respond(embed=self.inf_msg.set_lang_ok())
        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())
        
    @commands.slash_command(guild_only=True)
    async def set_player(self, ctx: commands.Context, 
            nickname: Option(
                str,
                description=Text().get().frequent.common.nickname,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.nickname,
                    'pl': Text().get('pl').frequent.common.nickname,
                    'uk': Text().get('ua').frequent.common.nickname
                },
                max_length=24,
                min_length=3,
                required=True
            ),
            region: Option(
                str,
                description=Text().get().frequent.common.region,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.region,
                    'pl': Text().get('pl').frequent.common.region,
                    'uk': Text().get('ua').frequent.common.region
                },
                choices=_config.default.available_regions,
                required=True
            )
        ):

        try:
            check_user(ctx)
        except UserBanned:
            return
        try:
            await ctx.defer()
            Text().load_from_context(ctx)
            
            try:
                game_id = await self.api.check_player(nickname, region)
            except api.NoPlayersFound:
                await ctx.respond(embed=ErrorMSG().player_not_found())
            except api.NeedMoreBattlesError:
                await ctx.respond(embed=ErrorMSG().need_more_battles())
            except api.APIError:
                await ctx.respond(embed=ErrorMSG().api_error())
            else:
                self.db.set_member(ctx.author.id, nickname, region, game_id)
                _log.debug(f'Set player: {ctx.author.id} {nickname} {region}')
                await ctx.respond(embed=self.inf_msg.set_player_ok())

        except Exception :
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())

    @commands.slash_command(guild_only=True)
    async def setup_server(
            self,
            ctx: commands.Context
        ):
        if not self.sdb.check_server(ctx.guild.id):
            self.sdb.set_new_server(ctx.guild.id, ctx.guild.name)
            await ctx.respond('`Set ok`')
        else:
            await ctx.respond('`Server already exist`')

    @commands.slash_command(guild_only=True)
    async def delite_server(
            self,
            ctx: commands.Context
        ):
        if self.sdb.check_server(ctx.guild.id):
            self.sdb.del_server(ctx.guild.id)
            await ctx.respond('`Delite ok`')
        else:
            await ctx.respond('`Server not exist`')

    @commands.slash_command(guild_only=True)
    async def set_background(
            self, 
            ctx: commands.Context,
            image: Option(
                Attachment,
                description=Text().get().cmds.set_background.descr.this,
                description_localizations={
                    'ru': Text().get('ru').cmds.set_background.descr.this,
                    'pl': Text().get('pl').cmds.set_background.descr.this,
                    'uk': Text().get('ua').cmds.set_background.descr.this
                },
                required=True
                ),
                server: Option(
                    bool,
                    description=Text().get().cmds.set_background.descr.sub_descr.server,
                    description_localizations={
                        'ru': Text().get('ru').cmds.set_background.descr.sub_descr.server,
                        'pl': Text().get('pl').cmds.set_background.descr.sub_descr.server,
                        'uk': Text().get('ua').cmds.set_background.descr.sub_descr.server
                    },
                    required=False
                )
            ):
        try:
            check_user(ctx)
        except UserBanned:
            return
        try:
            Text().load_from_context(ctx)
            image: Attachment = image
            await ctx.defer()

            if image.content_type not in ['image/png', 'image/jpeg']:
                await ctx.respond(
                    embed=self.err_msg.custom(
                        title=Text().get().frequent.errors.error,
                        text=Text().get().cmds.set_background.errors.file_error
                    )
                )
                return
            
            if image.size > 2_097_152:
                await ctx.respond(
                    embed=self.err_msg.custom(
                        title=Text().get().frequent.errors.error,
                        tetx=Text().get().cmds.set_background.errors.oversize
                    )
                )
                return
            
            if image.width > 2048 and image.height > 2048:
                await ctx.respond(
                    embed=self.err_msg.custom(
                        title=Text().get().frequent.errors.error,
                        text=Text().get().cmds.set_background.errors.overresolution
                    )
                )
                return
            
            if image.width < 256 and image.height < 256:
                await ctx.respond(
                    embed=self.err_msg.custom(
                        title=Text().get().frequent.errors.error,
                        text=Text().get().cmds.set_background.errors.small_resolution
                    )
                )
                return

            if server:
                if ctx.author.guild_permissions.administrator:
                    if self.sdb.check_server_premium(ctx.guild.id):
                        with io.BytesIO() as buffer:
                            await image.save(buffer)
                            pil_image = Image.open(buffer)
                            pil_image = resize_image(pil_image, (700, 1250))
                        with io.BytesIO() as buffer:
                            pil_image.save(buffer, format='PNG')
                            self.sdb.set_server_image(
                                base64.b64encode(buffer.getvalue()).decode(),
                                ctx
                            )
                            await ctx.respond(
                                embed=self.inf_msg.custom(
                                title=Text().get().frequent.info.info,
                                text=Text().get().cmds.set_background.info.set_background_ok,
                                colour='green'
                                )
                            )
                    else:
                        await ctx.respond(
                            embed=self.err_msg.custom(
                                title=Text().get().frequent.errors.error,
                                text=Text().get().cmds.set_background.errors.server_premium_not_found
                            )
                        )
                else:
                    await ctx.respond(
                        embed=self.err_msg.custom(
                            title=Text().get().frequent.errors.error,
                            text=Text().get().cmds.set_background.errors.permission_denied
                        )
                    )

            if self.db.check_member(ctx.author.id):
                if self.db.check_member_premium(ctx.author.id):
                    self.db.set_member_image(ctx.author.id, image)
                    with io.BytesIO() as buffer:
                        await image.save(buffer)
                        image = Image.open(buffer)
                        image = resize_image(image, (700, 1250))
                    with io.BytesIO() as buffer:
                        image.save(buffer, format='PNG')
                        self.db.set_member_image(
                            ctx.author.id,
                            base64.b64encode(buffer.getvalue()).decode()
                        )
                    await ctx.respond(
                        embed=self.inf_msg.custom(
                        title=Text().get().frequent.info.info,
                        text=Text().get().cmds.set_background.info.set_background_ok,
                        colour='green'
                        )
                    )
            else:
                await ctx.respond(
                    embed=self.err_msg.custom(
                        title=Text().get().frequent.errors.error,
                        tetx=Text().get().cmds.set_background.errors.player_not_registred
                        )
                    )
                
        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())

    @commands.slash_command(description='Test authorization')
    async def auth(self, ctx: commands.Context):
        await ctx.user.send(self.discord_oauth.auth_url)

def setup(bot):
    bot.add_cog(Set(bot))