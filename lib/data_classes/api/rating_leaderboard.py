from typing import List, Optional

from pydantic import BaseModel


class Neighbor(BaseModel):
    spa_id: int
    mmr: float
    season_number: int
    calibrationBattlesLeft: int
    number: int
    percentile: float
    skip: bool
    updated_at: str
    score: int
    league_index: int
    nickname: str
    clan_tag: str


class RatingLeaderboardAPIResponse(BaseModel):
    spa_id: int
    mmr: float
    season_number: int
    calibrationBattlesLeft: int
    number: Optional[int] = 0
    percentile: Optional[float] = None
    skip: bool
    updated_at: str
    neighbors: Optional[List[Neighbor]] = None
    score: int
    league_index: int
    nickname: str
    clan_tag: str
    clan_name: str