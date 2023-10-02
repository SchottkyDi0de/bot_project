import traceback

from discord import File, Option, Embed
from discord.ext import commands

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
        
    @commands.slash_command(description=Text().data.cmd_description.stats)
    async def stats(
            self, 
            ctx: commands.Context,
            nickname: Option(
                str,
                description=Text().data.cmd_description.nickname,
                required=True,
                max_lenght=24,
                min_lenght=3
            ),
            region: Option(
                str,
                description=Text().data.cmd_description.region,
                choices=Text().data.common.regions,
                required=True
            ),
        ):
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        try:
            await ctx.defer()
            Text().load(self.sdb.safe_get_lang(ctx.guild.id))
            
            img = await self.get_stats(nickname, region)
            if isinstance(img, Embed):
                await ctx.respond(embed=img)
            else:
                await ctx.respond(file=File(img, 'stats.png'))
                img.close()
        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error)

    @commands.slash_command(description=Text().data.cmd_description.astats)
    async def astats(self, ctx):
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        try:
            await ctx.defer()
            if not self.db.check_member(ctx.author.id):
                await ctx.respond(embed=InfoMSG().player_not_registred)
                
            else:
                Text().load(self.sdb.safe_get_lang(ctx.guild.id))
                player_data = self.db.get_member(ctx.author.id)
                img = await self.get_stats(player_data['nickname'], player_data['region'])
                if isinstance(img, Embed):
                    await ctx.respond(embed=img)
                else:
                    await ctx.respond(file=File(img, 'stats.png'))
                    img.close()
        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error)
    
    async def get_stats(self, nickname, region):
        try:
            try:
                data = await self.api.get_stats(nickname, region)
            except api.EmptyDataError:
                return ErrorMSG().unknown_error
            except api.NeedMoreBattlesError:
                return ErrorMSG().need_more_battles
            except api.UncorrectName:
                return ErrorMSG().uncorrect_name
            except api.UncorrectRegion:
                return ErrorMSG().uncorrect_region
            except api.NoPlayersFound:
                return ErrorMSG().player_not_found
            except api.APIError:
                return ErrorMSG().api_error
            except data_parser.DataParserError:
                return ErrorMSG().parser_error
            else:
                img_data = self.img_gen.generate(data)
                return img_data
        except Exception:
            _log.error(traceback.format_exc())


def setup(bot):
    bot.add_cog(Stats(bot))
