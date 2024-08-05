from discord import ApplicationContext
from pydantic import BaseModel, ConfigDict

from lib.data_classes.db_player import GameAccount, DBPlayer, AccountSlotsEnum


class MemberContext(BaseModel):
    game_account: GameAccount
    member: DBPlayer
    slot: AccountSlotsEnum


class MixedApplicationContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    m_ctx: MemberContext
    ctx: ApplicationContext
