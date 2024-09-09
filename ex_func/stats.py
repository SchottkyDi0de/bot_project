from io import BytesIO

from lib.data_classes.api.api_data import PlayerGlobalData
from lib.exceptions import api, data_parser

from lib.data_classes.db_player import AccountSlotsEnum, DBPlayer
from lib.locale.locale import Text

from .obj import Objects


class StatsFunc:
    @staticmethod
    async def get_stats(game_id: int, nickname: str, region: str) -> PlayerGlobalData | str:
        exception = None
        try:
            data = await Objects.api.get_stats(
                game_id=game_id,
                search=nickname,
                region=region
                )
        except* api.EmptyDataError:
            exception = Text().get().frequent.errors.unknown_error
        except* api.NeedMoreBattlesError:
            exception = Text().get().cmds.stats.errors.no_battles
        except* api.UncorrectName:
            exception = Text().get().cmds.stats.errors.uncorrect_nickname
        except* api.UncorrectRegion:
            exception = Text().get().frequent.errors.invalid_argument
        except* api.NoPlayersFound:
            exception = Text().get().cmds.stats.errors.player_not_found
        except* data_parser.DataParserError:
            exception = Text().get().frequent.errors.parser_error
        except* api.APIError:
            exception = Text().get().frequent.errors.api_error
        
        if exception:
            return exception

        return data

    @staticmethod
    async def stats4registred_player(slot: AccountSlotsEnum | str, member: DBPlayer) -> str | BytesIO:
        if isinstance(slot, str):
            slot = AccountSlotsEnum[slot]

        account = member.game_accounts.get_account_by_slot(slot)
        data = await StatsFunc.get_stats(account.game_id, account.nickname, account.region)

        if isinstance(data, str):
            return data

        return Objects.common_image_gen.generate(data, member, slot)
    
    @staticmethod
    async def generate_image(game_id: int, nickname: str, region: str) -> BytesIO | str:
        data = await StatsFunc.get_stats(game_id, nickname, region)

        if isinstance(data, str):
            return data

        return Objects.common_image_gen.generate(data)
