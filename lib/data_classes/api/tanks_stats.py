from typing import Optional

from pydantic import BaseModel


class All(BaseModel):
    spotted: int
    hits: int
    frags: int
    max_xp: int
    wins: int
    losses: Optional[int] = None
    capture_points: int
    battles: int
    damage_dealt: int
    damage_received: int
    max_frags: int
    shots: Optional[int] = None
    frags8p: int
    xp: int
    win_and_survived: int
    survived_battles: int
    dropped_capture_points: int

    winrate: Optional[float] = None
    avg_damage: Optional[int] = None
    accuracy: Optional[float] = None
    damage_ratio: Optional[float] = None
    destruction_ratio: Optional[float] = None
    frags_per_battle: Optional[float] = None
    avg_spotted: Optional[float] = None
    survival_ratio: Optional[float] = None


class TankStats(BaseModel):
    all: All
    last_battle_time: int
    account_id: int
    max_xp: int
    in_garage_updated: int
    max_frags: int
    frags: Optional[int]
    mark_of_mastery: int
    battle_life_time: int
    in_garage: Optional[bool]
    tank_id: int
