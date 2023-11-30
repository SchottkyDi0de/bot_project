from typing import Any, List, Optional

from pydantic import BaseModel


class Author(BaseModel):
    hitpoints_left: Optional[int]
    total_credits: int
    total_xp: int
    n_shots: int
    n_hits: int
    accuracy: Optional[float] = 0.0
    n_splashes: int
    n_penetrations: int
    penertarions_percent: Optional[float] = 0.0
    damage_dealt: int
    account_id: int
    team_number: int
    winner: Optional[bool] = None
    tank_id: Optional[int] = 0


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


class Clan(BaseModel):
    spotted: int
    max_frags_tank_id: int
    hits: int
    frags: int
    max_xp: int
    max_xp_tank_id: int
    wins: int
    losses: int
    capture_points: int
    battles: int
    damage_dealt: int
    damage_received: int
    max_frags: int
    shots: int
    frags8p: int
    xp: int
    win_and_survived: int
    survived_battles: int
    dropped_capture_points: int


class All(BaseModel):
    spotted: int
    max_frags_tank_id: Optional[int]
    hits: int
    frags: int
    max_xp: int
    max_xp_tank_id: Optional[int]
    wins: int
    losses: int
    winrate: Optional[float]
    capture_points: int
    battles: int
    damage_dealt: int
    damage_received: int
    max_frags: int
    shots: int
    frags8p: int
    xp: int
    win_and_survived: int
    survived_battles: int
    dropped_capture_points: int


class Statistics(BaseModel):
    clan: Optional[Clan] = None
    all: All


class PlayerResult(BaseModel):
    result_id: int
    info: Info2
    player_info: Optional[Info] = None
    statistics: Optional[Statistics] = None


class ParsedReplayData(BaseModel):
    mode_map_id: int
    map_name: Optional[str] = 'Undefined'
    timestamp_secs: int
    time_string: Optional[str] = '--/--'
    winner_team_number: int
    author: Author
    room_type: int
    room_name: Optional[str] = 'Undefined'
    free_xp: int
    players: List[Player]
    player_results: List[PlayerResult]