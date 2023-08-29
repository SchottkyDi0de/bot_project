from discord.ext import commands
from lib.database.discorddb import ServerDB
from datetime import datetime

__admin_ids = [
    766019191836639273
]

class AdminCommand(commands.Cog):

    @commands.command()
    async def get_sessions(self, ctx):
        if ctx.author.id in __admin_ids:
            db = ServerDB().db
            full_time_format = '%Y.%m.%d [%H:%M:%S]'
            timestamp_format = '[%H:%M:%S]'
            for i, j in enumerate(db.db["members"]):
                if db['members'][j]['last_stats'] == {}:
                    continue
                else:
                    timestamp = db['members'][j]['last_stats']['timestamp']
                    expiried_at = 43200 - (datetime.now().timestamp() - timestamp)

                    if expiried_at < 0:
                        expiried_at = datetime.utcfromtimestamp(-expiried_at).strftime(timestamp_format) + " Timestamp Expiried!"
                    else:
                        expiried_at = datetime.utcfromtimestamp(expiried_at).strftime(timestamp_format)

            ctx.respond(f"\n\
Timestamp: {datetime.utcfromtimestamp(timestamp).strftime(full_time_format)}\n\
User_id: {j}\n\
User_game_nickname: {db['members'][j]['nickname']}\n\
Expiried at: {expiried_at}")
            
def setup(bot):
    bot.add_cog(AdminCommand(bot))