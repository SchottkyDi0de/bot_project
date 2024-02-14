from pydantic import BaseModel


class Meta(BaseModel):
    count: int


class Clan(BaseModel):
    members_count: int
    name: str
    created_at: int
    tag: str
    clan_id: int
    emblem_set_id: int


class ClanData(BaseModel):
    role: str
    clan_id: int
    joined_at: int
    account_id: int
    account_name: str
    clan: Clan


class ClanStats(BaseModel):
    status: str
    meta: Meta
    data: ClanData
