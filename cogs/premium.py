from discord import Bot, InteractionContextType
from discord.ext import commands
from discord.commands import ApplicationContext

from lib.embeds.info import InfoMSG
from lib.locale.locale import Text
from lib.logger.logger import get_logger
from lib.views.alt_views import PremiumButtons

_log = get_logger(__file__, 'CogHelpLogger', 'logs/cog_help.log')


class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        contexts=[InteractionContextType.guild],
        description=Text().get('en').cmds.premium.descr.this,
        description_localizations={
            'ru': Text().get('ru').cmds.premium.descr.this,
            'pl': Text().get('pl').cmds.premium.descr.this,
            'uk': Text().get('ua').cmds.premium.descr.this
        }
    )
    async def premium(self, ctx: ApplicationContext):
        await Text().load_from_context(ctx)
        
        await ctx.respond(
            embed=InfoMSG().custom(
                Text().get(),
                title=Text().get().cmds.premium.items.main_msg_title,
                text=Text().get().cmds.premium.info.main_message,
                colour='yellow'
            ),
            view=PremiumButtons(Text().get()).get_view()
        )


def setup(bot: Bot):
    bot.add_cog(Premium(bot))
