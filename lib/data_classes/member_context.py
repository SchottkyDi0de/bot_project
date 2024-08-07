from discord import ApplicationContext
from pydantic import BaseModel, ConfigDict

from lib.data_classes.db_player import GameAccount, DBPlayer, AccountSlotsEnum


class MemberContext(BaseModel):
    game_account: GameAccount
    member: DBPlayer
    slot: AccountSlotsEnum


class MixedApplicationContext(ApplicationContext):
    def __init__(self, ctx: ApplicationContext, m_ctx: MemberContext):
        self.m_ctx: MemberContext = m_ctx
        self.ctx: ApplicationContext = ctx
