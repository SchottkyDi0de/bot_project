from random import randint
from io import StringIO

from discord import File, InteractionContextType, Option, Attachment, SelectOption
from discord.ext import commands

from lib.data_classes.member_context import MixedApplicationContext
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.locale.locale import Text
from lib.replay_parser.parser import ReplayParser
from lib.data_parser.parse_replay import ParseReplayData
from lib.logger.logger import get_logger
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.embeds.replay import EmbedReplayBuilder
from lib.exceptions.replay_parser import WrongFileType
from lib.error_handler.common import hook_exceptions
from lib.utils.commands_wrapper import with_user_context_wrapper
from lib.utils.replay_player_info import formatted_player_info
from lib.settings.settings import Config
from lib.views.alt_views import ReplayParser as ReplayParserView

_log = get_logger(__file__, 'CogReplayParserLogger', 'logs/cog_replay_parser.log')
_config = Config().get()

class CogReplayParser(commands.Cog):
    cog_command_error = hook_exceptions(_log)

    def __init__(self, bot):
        self.bot = bot
        self.sdb = ServersDB()
        self.pdb = PlayersDB()
        self.parser = ReplayParser()
        self.err_msg = ErrorMSG()
        self.inf_msg = InfoMSG()

    @commands.slash_command(
            contexts=InteractionContextType.guild,
            description=Text().get('en').cmds.parse_replay.descr.this,
            description_localizations={
                'ru': Text().get('ru').cmds.parse_replay.descr.this,
                'pl': Text().get('pl').cmds.parse_replay.descr.this,
                'uk': Text().get('ua').cmds.parse_replay.descr.this
            }
        )
    @commands.cooldown(1, 15, commands.BucketType.user)
    @with_user_context_wrapper('parse_replay')
    async def parse_replay(self,
            mixed_ctx: MixedApplicationContext,
            replay: Option(
                Attachment,
                description=Text().get('en').cmds.parse_replay.descr.sub_descr.file,
                description_localizations={
                    'ru': Text().get('ru').cmds.parse_replay.descr.sub_descr.file,
                    'pl': Text().get('pl').cmds.parse_replay.descr.sub_descr.file,
                    'uk': Text().get('ua').cmds.parse_replay.descr.sub_descr.file
                },
                required=True,
                
            ),
            region: Option(
                str,
                description=Text().get('en').frequent.common.region,
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
        ctx = mixed_ctx.ctx
        m_ctx = mixed_ctx.m_ctx
        
        await ctx.defer()
        
        member = m_ctx.member
        replay: Attachment = replay
        
        if not replay.filename.endswith('.wotbreplay'):
            raise WrongFileType('Wrong file type')

        filename = randint(1000000, 9999999)
        await replay.save(f'tmp/replay/{filename}.wotbreplay')

        if output_type == 'json':
            with StringIO(self.parser.parse(f'tmp/replay/{filename}.wotbreplay')) as f:
                await ctx.respond(file=File(f, 'replay_data.json'))
                
        elif output_type == 'embed':
            replay_data = await ParseReplayData().parse(
                self.parser.parse(f'tmp/replay/{filename}.wotbreplay'),
                region
            )
            
            choices = [
                SelectOption(
                    label=formatted_player_info(x),
                    value=str(x.info.account_id)
                ) for x in replay_data.player_results
            ]
            
            view = ReplayParserView(
                text=Text().get(),
                member=member,
                choices=choices,
                replay_data=replay_data,
                region=region
                ).get_view()
            
            await ctx.respond(
                embed=await EmbedReplayBuilder().build_embed(
                    ctx,
                    replay_data,
                    region=region
                ),
                view=view
            )


def setup(bot: commands.Bot):
    bot.add_cog(CogReplayParser(bot))