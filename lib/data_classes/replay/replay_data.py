from typing import List, Optional

from pydantic import BaseModel


class Author(BaseModel):
    hitpoints_left: Optional[int]
    total_credits: int
    total_xp: int
    n_shots: int
    n_hits: int
    n_splashes: int
    n_penetrations: int
    damage_dealt: int
    account_id: int
    team_number: int


class Info1(BaseModel):
    gfx_url: str
    gfx2_url: str
    kind: str


class Avatar(BaseModel):
    info: Info1


class Info(BaseModel):
    nickname: str
    platoon_id: Optional[int]
    team: int
    clan_tag: Optional[str]
    avatar: Avatar


class Player(BaseModel):
    account_id: int
    info: Info


class Info2(BaseModel):
    credits_earned: int
    base_xp: int
    n_shots: int
    n_hits_dealt: int
    n_penetrations_dealt: int
    damage_dealt: int
    damage_assisted_1: int
    damage_assisted_2: int
    n_hits_received: int
    n_non_penetrating_hits_received: int
    n_penetrations_received: int
    n_enemies_damaged: int
    n_enemies_destroyed: int
    victory_points_earned: int
    victory_points_seized: int
    account_id: int
    tank_id: int
    mm_rating: Optional[float]
    damage_blocked: int


class PlayerResult(BaseModel):
    result_id: int
    info: Info2


class ReplayData(BaseModel):
    mode_map_id: int
    timestamp_secs: int
    winner_team_number: int | None
    author: Author
    room_type: int
    free_xp: int
    players: List[Player]
    player_results: List[PlayerResult]