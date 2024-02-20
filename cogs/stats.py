from discord import File, Option
from discord.ext import commands

from lib.settings.settings import Config
from lib.image.common import ImageGen
from lib.locale.locale import Text
from lib.api.async_wotb_api import API
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.data_classes.db_player import ImageSettings
from lib.blacklist.blacklist import check_user
from lib.exceptions.error_handler.error_handler import error_handler
from lib.data_classes.db_server import ServerSettings
from lib.logger.logger import get_logger
from lib.utils.nickname_handler import handle_nickname, validate_nickname

_log = get_logger(__file__, 'CogStatsLogger', 'logs/cog_stats.log')


class Stats(commands.Cog):
    cog_command_error = error_handler(_log)

    def __init__(self, bot) -> None:
        self.bot = bot
        self.img_gen = ImageGen()
        self.api = API()
        self.db = PlayersDB()
        self.sdb = ServersDB()
        self.inf_msg = InfoMSG()
        self.err_msg = ErrorMSG()
        
    @commands.slash_command(
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
            ctx: commands.Context,
            nick_or_id: Option(
                str,
                description=Text().get('en').frequent.common.nickname,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.nickname,
                    'pl': Text().get('pl').frequent.common.nickname,
                    'uk': Text().get('ua').frequent.common.nickname
                },
                required=True,
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
                required=True
            ),
        ):
        Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()
        
        image_settings = None
        user_exist = self.db.check_member(ctx.author.id)
        if user_exist:
            image_settings = self.db.get_image_settings(ctx.author.id)
        else:
            image_settings = ImageSettings()
        
        server_settings = self.sdb.get_server_settings(ctx)
        
        nickname_type = validate_nickname(nick_or_id)
        
        composite_nickname = handle_nickname(nick_or_id, nickname_type)
        
        img = await self.get_stats(
            ctx, 
            region=region,
            nickname=composite_nickname.nickname,
            game_id=composite_nickname.player_id,
            image_settings=image_settings, 
            server_settings=server_settings
            )

        if img is not None:
            await ctx.respond(file=File(img, 'stats.png'))
            img.close()

    @commands.slash_command(
            description=Text().get('en').cmds.astats.descr.this,
            description_localizations={
                'ru': Text().get('ru').cmds.astats.descr.this,
                'pl': Text().get('pl').cmds.astats.descr.this,
                'uk': Text().get('ua').cmds.astats.descr.this
                }
            )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def astats(self, ctx: commands.Context):
        Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()
        
        if not self.db.check_member(ctx.author.id):
            await ctx.respond(embed=self.inf_msg.player_not_registred_astats())
            
        else:
            player_data = self.db.get_member(ctx.author.id)
            if player_data is not None:
                image_settings = self.db.get_image_settings(ctx.author.id)
                server_settings = self.sdb.get_server_settings(ctx)
                img = await self.get_stats(
                    ctx,
                    region=player_data.region,
                    game_id=player_data.game_id, 
                    image_settings=image_settings, 
                    server_settings=server_settings
                    )

                if img is not None:
                    await ctx.respond(file=File(img, 'stats.png'))
                    img.close()
                else:
                    raise TypeError('Image is None')

    
    async def get_stats(
            self, 
            ctx: commands.Context, 
            image_settings: ImageSettings, 
            server_settings: ServerSettings,
            region: str,
            game_id: int | None = None,
            nickname: str | None = None, 
        ):
        try:
            data = await self.api.get_stats(
                game_id=game_id, search=nickname, region=region
                )
        except ExceptionGroup as exc:
            raise exc.exceptions[0]
        img_data = self.img_gen.generate(ctx, data, image_settings, server_settings)
        return img_data


def setup(bot):
    bot.add_cog(Stats(bot))
