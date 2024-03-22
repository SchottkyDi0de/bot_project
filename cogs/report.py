from discord import Cog, Option
from discord.ext import commands
from discord.commands import ApplicationContext

from lib.blacklist.blacklist import check_user
from lib.locale.locale import Text
from lib.logger.logger import get_logger
from lib.error_handler.common import hook_exceptions
from lib.utils.views import ViewMeta

_log = get_logger(__file__, 'CogReportLogger', 'logs/cog_report.log')


class Report(Cog):
    cog_command_error = hook_exceptions(_log)
    
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
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def report(
        self, ctx: ApplicationContext, 
        report_type: Option(
            str,
            description=Text().get('en').cmds.report.descr.sub_descr.type,
            description_localizations={
                'ru': Text().get('ru').cmds.report.descr.sub_descr.type,
                'pl': Text().get('pl').cmds.report.descr.sub_descr.type,
                'uk': Text().get('ua').cmds.report.descr.sub_descr.type 
                },
                required=True,
                choices=["bug_report", "suggestion"]
            )
        ):
        Text().load_from_context(ctx)
        check_user(ctx)

        await ctx.send_modal(ViewMeta(self.bot, ctx, 'report', report_type={"bug_report": "b", "suggestion": "s"}[report_type]))
        await ctx.respond("👍", ephemeral=True)
        

    
def setup(bot):
    bot.add_cog(Report(bot))
