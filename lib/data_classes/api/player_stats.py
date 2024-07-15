from typing import Optional

from pydantic import BaseModel


class Meta(BaseModel):
    count: int


class Rating(BaseModel):
    
    spotted: int
    calibration_battles_left: int
    hits: int
    frags: int
    recalibration_start_time: int
    mm_rating: Optional[float] = None
    wins: int
    losses: int
    is_recalibration: bool
    capture_points: int
    battles: int
    current_season: int
    damage_dealt: int
    damage_received: int
    shots: int
    frags8p: int
    xp: int
    win_and_survived: int
    survived_battles: int
    dropped_capture_points: int
    max_xp: Optional[int] = None
    max_xp_tank_id: Optional[int] = None

    rating: Optional[int] = None
    avg_xp: Optional[int] = None
    avg_damage: Optional[int] = None
    accuracy: Optional[float] = None
    winrate: Optional[float] = None
    avg_spotted: Optional[float] = None
    frags_per_battle: Optional[float] = None
    not_survived_battles: Optional[int] = None
    survival_ratio: Optional[float] = None
    damage_ratio: Optional[float] = None
    destruction_ratio: Optional[float] = None
    leaderboard_position: Optional[int] = None


class All(BaseModel):
    spotted: int
    max_frags_tank_id: int
    hits: int
    max_frags: int
    frags: int
    wins: int
    losses: int
    capture_points: int
    battles: int
    damage_dealt: int
    damage_received: int
    shots: int
    frags8p: int
    xp: int
    win_and_survived: int
    survived_battles: int
    dropped_capture_points: int
    max_xp: int
    max_xp_tank_id: Optional[int] = None

    avg_xp: Optional[int] = None
    avg_damage: Optional[int] = None
    accuracy: Optional[float] = None
    winrate: Optional[float] = None
    avg_spotted: Optional[float] = None
    frags_per_battle: Optional[float] = None
    not_survived_battles: Optional[int] = None
    survival_ratio: Optional[float] = None
    damage_ratio: Optional[float] = None
    destruction_ratio: Optional[float] = None


class Statistics(BaseModel):
    rating: Optional[Rating] = None
    all: All


class PlayerData(BaseModel):
    statistics: Statistics
    nickname: str
    account_id: int
    created_at: int
    updated_at: int
    private: Optional[bool] = None
    last_battle_time: Optional[int] = None


class PlayerStats(BaseModel):
    status: str
    meta: Meta
    data: PlayerData
