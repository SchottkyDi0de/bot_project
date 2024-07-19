import discord
from discord.ext import commands
from discord import ApplicationContext, Bot

from lib.database.players import PlayersDB
from lib.data_classes.db_player import UsedCommand
from lib.error_handler.common import hook_exceptions
from lib.image.profile import ProfileImageGen
from lib.logger.logger import get_logger
from lib.utils.calculate_exp import get_level
from lib.utils.standard_account_validate import standard_account_validate
from lib.locale.locale import Text
from lib.image.utils.b64_img_handler import base64_to_ds_file

_log = get_logger(__file__, 'CogProfileLogger', 'logs/cog_profile.log')


class Profile(commands.Cog):
    cog_command_error = hook_exceptions(_log)
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = PlayersDB()
        
    @commands.slash_command(name="profile", description="Get information about your account")
    async def profile(
        self, 
        ctx: ApplicationContext,
        user: discord.Option(
            discord.Member,
            description="Get information about another account",
            required=False,
            default=None
            )
        ):
        await ctx.defer()
        await Text().load_from_context(ctx)
        user: discord.Member = user
        
        if user is None:
            _, member, _ = await standard_account_validate(account_id=ctx.user.id, slot=None)
            await self.db.set_analytics(UsedCommand(name=ctx.command.name), member=member)
        
        else:
            _, member, _ = await standard_account_validate(account_id=user.id, slot=None)
        
        username = user.display_name if user is not None else ctx.user.display_name
        image = ProfileImageGen().generate(member=member, username=username)
        level_info = get_level(member.profile.level_exp)
        
        await ctx.respond(
            f'`Level {level_info.level} ({level_info.rem_exp} / {level_info.next_exp})`',
            file=base64_to_ds_file(image, 'profile.png'),
        )


def setup(bot: Bot):
    bot.add_cog(Profile(bot))
