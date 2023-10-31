import traceback
from random import randint
from io import StringIO
import os

from discord import File, Option, Attachment
from discord.ext import commands

from lib.blacklist.blacklist import check_user
from lib.exceptions.blacklist import UserBanned
from lib.database.servers import ServersDB
from lib.locale.locale import Text
from lib.replay_parser.parser import ReplayParser
from lib.replay_parser.parser import ReplayParserError
from lib.logger.logger import get_logger
from lib.embeds.errors import ErrorMSG

_log = get_logger(__name__, 'CogReplayParserLogger', 'logs/cog_replay_parser.log')

class CogReplayParser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sdb = ServersDB()
        self.parser = ReplayParser()

    @commands.slash_command(
            guild_only=True, 
            description='Parse replay (TESTING...)',
            description_localizations={
                'ru': 'Парсинг реплея (ТЕСТИРОВАНИЕ...)',
            })
    async def parse_replay(self,
                    ctx: commands.Context,
                    replay: Option(
                        Attachment,
                        description='Attach the replay file (.wotbreplay)',
                        required=True,
                        
                    ),
                    output_type: Option(
                        str,
                        description='Output type',
                        choices=['raw (json)', ],
                        required=True
                    )
                ):
        Text().load(self.sdb.safe_get_lang(ctx.guild.id))
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        try:
            await ctx.defer()

            if not isinstance(replay, Attachment):
                await ctx.respond('`Uncorrect file!`')
                return
            
            filename = randint(1000000, 9999999)
            await replay.save(f'tmp/replay/{filename}.wotbreplay')

            match output_type:
                case 'raw (json)':
                    with StringIO(self.parser.parse(f'tmp/replay/{filename}.wotbreplay')) as f:
                        await ctx.respond(file=File(f, 'replay_data.json'))
            
            os.remove(f'tmp/replay/{filename}.wotbreplay')                

        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(embed=ErrorMSG().unknown_error)

def setup(bot):
    bot.add_cog(CogReplayParser(bot))