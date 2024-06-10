from discord import File, Option, Bot
from discord.ext import commands
from discord.commands import ApplicationContext

from lib.settings.settings import Config
from lib.image.common import ImageGenCommon
from lib.locale.locale import Text
from lib.api.async_wotb_api import API
from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.data_classes.db_player import AccountSlotsEnum, DBPlayer, GameAccount, ImageSettings
from lib.blacklist.blacklist import check_user
from lib.exceptions import api, data_parser
from lib.error_handler.common import hook_exceptions
from lib.data_classes.db_server import DBServer, ServerSettings
from lib.logger.logger import get_logger
from lib.utils.nickname_handler import handle_nickname
from lib.utils.validators import validate
from lib.utils.standard_account_validate import standard_account_validate

_log = get_logger(__file__, 'CogStatsLogger', 'logs/cog_stats.log')


class Stats(commands.Cog):
    cog_command_error = hook_exceptions(_log)

    def __init__(self, bot) -> None:
        self.bot = bot
        self.img_gen = ImageGenCommon()
        self.api = API()
        self.db = PlayersDB()
        self.sdb = ServersDB()
        self.inf_msg = InfoMSG()
        self.err_msg = ErrorMSG()
        
    @commands.slash_command(
        description=Text().get('en').cmds.stats.descr.this,
        description_localizations={
            'ru' : Text().get('ru').cmds.stats.descr.this,
            'pl' : Text().get('pl').cmds.stats.descr.this,
            'uk' : Text().get('ua').cmds.stats.descr.this
            }
        )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stats(
            self, 
            ctx: ApplicationContext,
            nick_or_id: Option(
                str,
                description=Text().get('en').frequent.common.nickname,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.nickname,
                    'pl': Text().get('pl').frequent.common.nickname,
                    'uk': Text().get('ua').frequent.common.nickname
                },
                required=True,
            ), # type: ignore
            region: Option(
                str,
                description=Text().get('en').frequent.common.region,
                description_localizations={
                    'ru': Text().get('ru').frequent.common.region,
                    'pl': Text().get('pl').frequent.common.region,
                    'uk': Text().get('ua').frequent.common.region
                },
                choices=Config().get().default.available_regions,
                required=True
            ), # type: ignore
        ):
        await Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()
        
        member = await self.db.check_member_exists(ctx.author.id, raise_error=False, get_if_exist=True)
        member = None if isinstance(member, bool) else member
        
        nickname_type = validate(nick_or_id, 'nickname')
        composite_nickname = handle_nickname(nick_or_id, nickname_type)
        
        img = await self.get_stats(
            ctx, 
            region=region,
            nickname=composite_nickname.nickname,
            game_id=composite_nickname.player_id,
            requested_by=member,
            server=self.sdb.get_server(ctx)
        )

        if img is not None:
            await ctx.respond(file=File(img, 'stats.png'))
            img.close()
        else:
            _log.error('Image gen returned None')
            raise RuntimeError('Image gen returned None')

    @commands.slash_command(
            description=Text().get('en').cmds.astats.descr.this,
            description_localizations={
                'ru': Text().get('ru').cmds.astats.descr.this,
                'pl': Text().get('pl').cmds.astats.descr.this,
                'uk': Text().get('ua').cmds.astats.descr.this
                }
            )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def astats(
        self, 
        ctx: ApplicationContext,
        account: Option(
            int,
            description=Text().get('en').frequent.common.slot,
            description_localizations={
                'ru': Text().get('ru').frequent.common.slot,
                'pl': Text().get('pl').frequent.common.slot,
                'uk': Text().get('ua').frequent.common.slot
            },
            required=False,
            default=None,
            choices=[x.value for x in AccountSlotsEnum]
            )
        ) -> None:
        await Text().load_from_context(ctx)
        check_user(ctx)
        await ctx.defer()
        
        game_account, member, slot = await standard_account_validate(ctx.author.id, slot=account)
        server = self.sdb.get_server(ctx)
        
        img = await self.get_stats(
            ctx,
            region=game_account.region,
            game_id=game_account.game_id, 
            slot=slot,
            server=server,
            requested_by=member
            )

        if img is not None:
            await ctx.respond(file=File(img, 'stats.png'))
            img.close()
        else:
            return

    
    async def get_stats(
            self, 
            ctx: ApplicationContext, 
            region: str,
            server: DBServer | None = None,
            slot: AccountSlotsEnum | None = None,
            game_id: int | None = None,
            nickname: str | None = None,
            requested_by: DBPlayer | None = None
        ):
        exception = None
        try:
            data = await self.api.get_stats(
                game_id=game_id,
                search=nickname,
                region=region,
                requested_by=requested_by
                )
        except* api.EmptyDataError:
            exception = 'unknown_error'
        except* api.NeedMoreBattlesError:
            exception = 'need_more_battles'
        except* api.UncorrectName:
            exception = 'uncorrect_name'
        except* api.UncorrectRegion:
            exception = 'uncorrect_region'
        except* api.NoPlayersFound:
            exception = 'player_not_found'
        except* data_parser.DataParserError:
            exception = 'parser_error'
        except* api.LockedPlayer as exc:
            exception = 'locked_player'
        except* api.APIError:
            exception = 'api_error'
            
        if exception is not None:
            await ctx.respond(embed=getattr(self.err_msg, exception)())
            return
        else:
            img_data = self.img_gen.generate(
                data=data,
                server=server,
                member=requested_by,
                slot=slot
            )
            return img_data


def setup(bot: Bot):
    bot.add_cog(Stats(bot))
