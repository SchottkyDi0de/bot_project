import os.path, sys

from discord import File, Option, Embed
from discord.ext import commands
# from time import time

from lib.exceptions import api, data_parser, database
from lib.image.common import ImageGen
from lib.locale.locale import Text
from lib.api.async_wotb_api import API
from lib.embeds import errors, info
from lib.database import discorddb

class Stats(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.img_gen = ImageGen()
        self.api = API()
        self.err_msg = errors.ErrorMSG()
        self.inf_msg = info.InfoMSG()
        self.db = discorddb.ServerDB()
        
    @commands.slash_command(description=Text().data.cmd_description.stats)
    async def stats(
            self, 
            ctx,
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
        await ctx.defer()
        img = await self.get_stats(nickname, region)
        if isinstance(img, Embed):
            await ctx.respond(embed=img)
        else:
            await ctx.respond(file=File(img, 'stats.png'))
            img.close()
        
    @commands.slash_command(description=Text().data.cmd_description.astats)
    async def astats(self, ctx):
        await ctx.defer()
        if not self.db.check_member(ctx.author.id):
            await ctx.respond(embed=self.inf_msg.player_not_registred)
            
        else:
            player_data = self.db.get_member(ctx.author.id)
            img = await self.get_stats(player_data['nickname'], player_data['region'])
            if isinstance(img, Embed):
                await ctx.respond(embed=img)
            else:
                await ctx.respond(file=File(img, 'stats.png'))
                img.close()
    
    async def get_stats(self, nickname, region):
        try:
            data = await self.api.get_stats(nickname, region)
        except api.EmptyDataError:
            return self.err_msg.unknown_error
        except api.NeedMoreBattlesError:
            return self.err_msg.need_more_battles
        except api.UncorrectName:
            return self.err_msg.uncorrect_name
        except api.UncorrectRegion:
            return self.err_msg.uncorrect_region
        except api.NoPlayersFound:
            return self.err_msg.player_not_found
        except api.APIError:
            return self.err_msg.api_error
        except data_parser.DataParserError:
            return self.err_msg.parser_error
        else:
            img_data = self.img_gen.generate(data)
            return img_data

    
def setup(bot):
    bot.add_cog(Stats(bot))