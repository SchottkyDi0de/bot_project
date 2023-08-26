import os.path, sys

from discord import File, Option
from discord.ext import commands

from lib.exceptions import database
from lib.database import discorddb
from lib.locale.locale import Text
from lib.embeds import errors, info

class Set(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = discorddb.ServerDB()
        self.inf_msg = info.InfoMSG()
        self.err_msg = errors.ErrorMSG()
        
    @commands.slash_command(guild_only=True)
    async def set_lang(self, ctx, 
            lang: Option(
                str,
                description=Text().data.cmd_description.lang,
                choices=Text().data.common.langs,
                required=True
            )
        ):
        pass  # Не забудь...
        
    @commands.slash_command(guild_only=True)
    async def set_player(self, ctx, 
            nickname: Option(
                str,
                description=Text().data.cmd_description.nickname,
                max_length=24,
                min_length=3,
                required=True
            ),
            region: Option(
                str,
                description=Text().data.cmd_description.region,
                choices=Text().data.common.regions,
                required=True
            )
        ):
        await ctx.defer()
        self.db.set_member(ctx.author.id, nickname, region)
        await ctx.respond(embed=self.inf_msg.set_player_ok)
        

    
def setup(bot):
    bot.add_cog(Set(bot))