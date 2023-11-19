import os
import traceback

from discord.ext import commands
from discord import Bot
from lib.logger.logger import get_logger
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from datetime import datetime
from lib.blacklist import blacklist

_admin_ids = [
    766019191836639273
]

_log = get_logger(__name__, 'AdminCogLogger', 'logs/admin.log')


class AdminCommand(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.extension_names = []

        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                self.extension_names.append(f"cogs.{filename[:-3]}")

    @commands.command()
    async def say_direct(self, ctx):
        if ctx.author.id in _admin_ids:
            try:
                data = ctx.message.content.split('/')
                if len(data) != 4:
                    await ctx.author.send('```Uncorrect command format\n!say_direct/<!text: message>/<!guild: guild_id>/<!member: member_id or mention>```')
                    return
                
                text, guild_id, target = data[1], data[2], data[3]
                if type(target) == str:
                    guild = self.bot.get_guild(int(guild_id))
                    user = guild.get_member(int(target))

                if user is None:
                    await ctx.author.send('`Member not found or private`')
                    return
                
                await user.send(text)
            
            except Exception:
                await ctx.author.send(f'```{traceback.format_exc()}```')

    @commands.command()
    async def show_blacklist(self, ctx: commands.Context):
        msg = ctx.message.content
        if len(msg) == 2:
            if msg[1].lower() == 'this':
                text = ''
                for i in blacklist.data:
                    text += f'<@{str(i)}\n>'
                ctx.reply(text)
            else:
                await ctx.author.send(text)
            return
        await ctx.author.send(f'<@{str(i)}\n>')

    @commands.command()
    async def blacklist(self, ctx: commands.Context):
        if ctx.author.id in _admin_ids:
            try:
                msg = ctx.message.content.split(' ')
                if len(msg) > 3:
                    await ctx.author.send('```Uncorrect command format\n!blacklist [ID: Integer] {Add|Remove: Option(String)}```')
                    return
                
                elif len(msg) == 3:
                    if msg[2].lower == 'add':
                        blacklist.data.append(msg[1])
                        await ctx.author.send(f'`{msg[1]} added in blacklist`')
                    elif msg[2].lower == 'remove':
                        blacklist.data.remove(msg[1])
                        await ctx.author.send(f'`{msg[1]} removed in blacklist`')
                    blacklist.reload()
                
                elif len(msg) == 2:
                    blacklist.data.append(msg[1])
                    await ctx.author.send(f'`{msg[1]} added in blacklist`)')
                    blacklist.reload()
                
                else:
                    await ctx.author.send('```Uncorrect command format\n!blacklist [ID: Integer] {Add|Remove: String}```')
            
            except Exception:
                _log.error(traceback.format_exc())
                ctx.author.send()


    @commands.command()
    async def say(self, ctx):
        if ctx.author.id in _admin_ids:
            try:
                data = ctx.message.content.split('/')
                if len(data) != 3:
                    await ctx.author.send('```Uncorrect command format\n!say/<!text: message>/<!target: channel_id>```')
                    return
                
                text, target = data[1], data[2]
                channel = self.bot.get_channel(int(target))
                await channel.send(text)
            except AttributeError:
                await ctx.author.send('`Channel not found or private`')
            except Exception:
                await ctx.author.send(f'```{traceback.format_exc()}```')
            else:
                ctx.author.send('`Message sent successfully`')

    @commands.command()
    async def get_member(self, ctx):
        if ctx.author.id in _admin_ids:
            try:
                db = PlayersDB()
                member_id: str = ctx.message.content
                member_id = member_id.split(' ')
                await ctx.send(f'`{db.get_member(int(member_id[1]))}`')
            except:
                await ctx.send(f'`{traceback.format_exc()}`')

    @commands.command()
    async def get_members(self, ctx):
        if ctx.author.id in _admin_ids:
            try:
                db = PlayersDB()
                for i, j in enumerate(db.db['members']):
                    await ctx.author.send(
                        f"```Player_id: {db.db['members'][j]['id']}"
                        f"Player_nickname: {db.db['members'][j]['nickname']}"
                        f"Region: {db.db['members'][j]['region']}"
                        f"lang{db.db['members'][j]['lang']}```"
                        )
                await ctx.author.send(f"`Count: {i+1}`")
            except Exception:
                await ctx.author.send(traceback.format_exc())

    @commands.command()
    async def get_servers(self, ctx):
        if ctx.author.id in _admin_ids:
            try:
                sdb = ServersDB()
                for i, j in enumerate(sdb.db['servers']):
                    await ctx.author.send(f"```Server_id: {sdb.db['servers'][j]['id']}\n Server_name: {sdb.db['servers'][j]['name']}\nSettings: {sdb.db['servers'][j]['settings']}```")
                await ctx.author.send(f"`count: {i+1}`")
            except Exception:
                await ctx.author.send(f'```{traceback.format_exc()}```')

    @commands.command()
    async def get_sessions(self, ctx):
        if ctx.author.id in _admin_ids:
            try:
                db = PlayersDB().db
                full_time_format = '%Y.%m.%d [%H:%M:%S]'
                timestamp_format = '[%H:%M:%S]'
                for i, j in enumerate(db.db["members"]):
                    if db['members'][j]['last_stats'] == {}:
                        await ctx.author.send(f'```Member: {j} has no session stats```')
                    else:
                        timestamp = db['members'][j]['last_stats']['timestamp']
                        expiried_at = 43200 - (datetime.now().timestamp() - timestamp)

                        if expiried_at < 0:
                            expiried_at = datetime.utcfromtimestamp(-expiried_at).strftime(timestamp_format) + " Timestamp Expiried!"
                        else:
                            expiried_at = datetime.utcfromtimestamp(expiried_at).strftime(timestamp_format)

                        await ctx.author.send(f"\n\
```No: {i}\n\
Timestamp: {datetime.utcfromtimestamp(timestamp).strftime(full_time_format)}\n\
User_id: {j}\n\
User_game_nickname: {db['members'][j]['nickname']}\n\
Expiried at: {expiried_at}```")
            except Exception:
                await ctx.author.send(f'```{traceback.format_exc()}```')

    @commands.command()
    async def reload_ext(self, ctx, extension_name: str):
        if ctx.author.id in _admin_ids:
            self.bot.load_extension(extension_name)
            await ctx.author.send(f'`Extension {extension_name} reloaded`')
            _log.info(f'Extension {extension_name} reloaded!')

    @commands.command()
    async def reload_ext_all(self, ctx):
        if ctx.author.id in _admin_ids:
            for i in self.extension_names:
                self.bot.reload_extension(i)

            await ctx.author.send('`Extensions reloaded`')
            _log.info('Extensions reloaded!')

def setup(bot):
    bot.add_cog(AdminCommand(bot))