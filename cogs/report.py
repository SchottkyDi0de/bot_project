from discord import Cog
from discord.ext import commands

from lib.locale.locale import Text
from lib.utils.views import ViewMeta


class Report(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(
        description=Text().get('en').cmds.report.descr.this,
        description_localizations={
            'ru' : Text().get('ru').cmds.report.descr.this,
            'pl' : Text().get('pl').cmds.report.descr.this,
            'uk' : Text().get('ua').cmds.report.descr.this
            }
    )
    async def report(self, ctx: commands.Context):
        Text().load_from_context(ctx)

        await ctx.send_modal(ViewMeta(self.bot, ctx, 'report'))
        await ctx.respond("👍", ephemeral=True)
        

    
def setup(bot):
    bot.add_cog(Report(bot))
