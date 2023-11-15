import traceback

from discord import File, Option, Embed
from discord.ext import commands

from lib.settings.settings import Config
from lib.exceptions import api, data_parser
from lib.image.common import ImageGen
from lib.locale.locale import Text
from lib.api.async_wotb_api import API
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.blacklist.blacklist import check_user
from lib.exceptions.blacklist import UserBanned
from lib.logger.logger import get_logger

_log = get_logger(__name__, 'CogStatsLogger', 'logs/cog_stats.log')


class Stats(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.img_gen = ImageGen()
        self.api = API()
        self.db = PlayersDB()
        self.sdb = ServersDB()
        self.inf_msg = InfoMSG()
        self.err_msg = ErrorMSG()
        
    @commands.slash_command(
            description=Text().get().cmds.stats.descr.this,
            description_localizations={
                'ru' : Text().get('ru').cmds.stats.descr.this
                }
            )
    async def stats(
            self, 
            ctx: commands.Context,
            nickname: Option(
                str,
                description=Text().get().frequent.common.nickname,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.nickname
                },
                required=True,
                max_lenght=24,
                min_lenght=3
            ),
            region: Option(
                str,
                description=Text().get().frequent.common.region,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.region
                },
                choices=Config().get().default.available_regions,
                required=True
            ),
        ):
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        try:
            await ctx.defer()
            Text().load_from_context(ctx)
            img = await self.get_stats(ctx, nickname, region)

            if img is not None:
                await ctx.respond(file=File(img, 'stats.png'))
                img.close()

        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())

    @commands.slash_command(
            description=Text().get().cmds.astats.descr.this,
            description_localizations={
                'ru': Text().get('ru').cmds.astats.descr.this
                }
            )
    async def astats(self, ctx: commands.Context):
        try:
            check_user(ctx)
        except UserBanned:
            return
        _log.debug(f'User locale is: {ctx.interaction.locale}')
        
        Text().load_from_context(ctx)
        try:
            await ctx.defer()
            if not self.db.check_member(ctx.author.id):
                await ctx.respond(embed=self.inf_msg.player_not_registred_astats())
                
            else:
                player_data = self.db.get_member(ctx.author.id)
                img = await self.get_stats(ctx, player_data['nickname'], player_data['region'])

                if img is not None:
                    await ctx.respond(file=File(img, 'stats.png'))
                    img.close()

        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=self.err_msg.unknown_error())
    
    async def get_stats(self, ctx: commands.Context, nickname: str, region: str):
        exception = None
        try:
            data = await self.api.get_stats(nickname, region)
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
        except* api.APIError:
            exception = 'api_error'
        except* data_parser.DataParserError:
            exception = 'parser_error'
        if exception is not None:
            await ctx.respond(embed=getattr(self.err_msg, exception)())
            return None
        else:
            img_data = self.img_gen.generate(data)
            return img_data


def setup(bot):
    bot.add_cog(Stats(bot))
