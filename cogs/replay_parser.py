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
from lib.data_parser.parse_replay import ParseReplayData
from lib.logger.logger import get_logger
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.embeds.replay import EmbedReplayBuilder
from lib.settings.settings import Config

_log = get_logger(__name__, 'CogReplayParserLogger', 'logs/cog_replay_parser.log')
_config = Config().get()

class CogReplayParser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sdb = ServersDB()
        self.parser = ReplayParser()

    @commands.slash_command(
            guild_only=True, 
            description=Text().get().cmds.parse_replay.descr.this,
            description_localizations={
                'ru': Text().get('ru').cmds.parse_replay.descr.this,
                'pl': Text().get('pl').cmds.parse_replay.descr.this,
                'uk': Text().get('ua').cmds.parse_replay.descr.this
            }
        )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def parse_replay(self,
                    ctx: commands.Context,
                    replay: Option(
                        Attachment,
                        description=Text().get().cmds.parse_replay.descr.sub_descr.file,
                        description_localizations={
                            'ru': Text().get('ru').cmds.parse_replay.descr.sub_descr.file,
                            'pl': Text().get('pl').cmds.parse_replay.descr.sub_descr.file,
                            'uk': Text().get('ua').cmds.parse_replay.descr.sub_descr.file
                        },
                        required=True,
                        
                    ),
                    region: Option(
                        str,
                        description=Text().get().frequent.common.region,
                        description_localizations={
                            'ru': Text().get('ru').frequent.common.region,
                            'pl': Text().get('pl').frequent.common.region,
                            'uk': Text().get('ua').frequent.common.region
                        },
                        required=True,
                        choices=_config.default.available_regions
                    ),
                    output_type: Option(
                        str,
                        description='Output type',
                        choices=['raw (json)', 'embed'],
                        default='embed',
                    ),
                ):
        Text().load_from_context(ctx)
        try:
            check_user(ctx)
        except UserBanned:
            return
        
        try:
            await ctx.defer()
            
            filename = randint(1000000, 9999999)
            await replay.save(f'tmp/replay/{filename}.wotbreplay')

            match output_type:
                case 'raw (json)':
                    with StringIO(self.parser.parse(f'tmp/replay/{filename}.wotbreplay')) as f:
                        await ctx.respond(file=File(f, 'replay_data.json'))
                case 'embed':
                    replay_data = await ParseReplayData().parse(
                                self.parser.parse(f'tmp/replay/{filename}.wotbreplay'),
                                region
                            )
                    await ctx.respond(
                        embed=EmbedReplayBuilder().build_embed(
                            ctx,
                            replay_data
                            )
                        )             

        except Exception:
            _log.error(traceback.format_exc())
            await ctx.respond(
                embed=ErrorMSG().custom(
                    title=Text().get().frequent.errors.error,
                    text=Text().get().cmds.parse_replay.errors.parsing_error
                    )
                )
    
    @parse_replay.error
    async def on_error(self, ctx: commands.Context, _):
        _log.error(traceback.format_exc())
        await ctx.respond(
            embed=InfoMSG().cooldown_not_expired()
            )

def setup(bot):
    bot.add_cog(CogReplayParser(bot))