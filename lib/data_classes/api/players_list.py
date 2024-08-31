from typing import List
from pydantic import BaseModel


class PlayerListItem(BaseModel):
    nickname: str
    account_id: int


class PlayerSearchResult(BaseModel):
    data = List[PlayerListItem]
