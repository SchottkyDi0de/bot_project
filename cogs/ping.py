from discord.ext import commands

from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.locale.locale import Text
from lib.image.common import ImageGen


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping(self, ctx):
        try:
            await ctx.defer()
            response_time, image_gen_time = await ImageGen().speed_test()
            if response_time == 0 or image_gen_time == 0:
                await ctx.respond(f'`Bot latency: {round(self.bot.latency, 4)} sec`')
                return
            
            await ctx.respond(f'```py\n'
                            f'Bot latency:           |  {round(self.bot.latency, 3)} sec\n'
                            f'API Response time:     |  {response_time} sec\n'
                            f'Image generation time: |  {image_gen_time} sec\n'
                            f'```')
        except:
            await ctx.respond(embed=ErrorMSG().unknown_error())
    
    @ping.error
    async def on_error(self, ctx: commands.Context, _):
        await ctx.respond(
            embed=InfoMSG().cooldown_not_expired()
            )

def setup(bot):
    bot.add_cog(Ping(bot))