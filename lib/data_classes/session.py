from pydantic import BaseModel


class TankSessionData(BaseModel):
    tank_name: str
    tank_tier: int
    tank_type: str
    tank_id: int
    
    d_hits: int
    d_frags: int
    d_wins: int
    d_losses: int
    d_capture_points: int
    d_damage_dealt: int
    d_damage_received: int
    d_shots: int
    d_xp: int
    d_survived_battles: int
    d_dropped_capture_points: int
    
    d_winrate: float
    d_avg_damage: int
    d_battles: int
    d_accuracy: float
    d_damage_ratio: float
    d_destruction_ratio: float
    d_frags_per_battle: float
    d_survival_ratio: float
    d_avg_spotted: float
    
    s_hits: int
    s_frags: int
    s_wins: int
    s_losses: int
    s_capture_points: int
    s_damage_dealt: int
    s_damage_received: int
    s_shots: int
    s_xp: int
    s_survived_battles: int
    s_dropped_capture_points: int
    
    s_winrate: float
    s_avg_damage: int
    s_battles: int
    s_accuracy: float
    s_damage_ratio: float
    s_destruction_ratio: float
    s_frags_per_battle: float
    s_survival_ratio: float
    s_avg_spotted: float


class MainDiff(BaseModel):
    hits: int
    frags: int
    wins: int
    losses: int
    capture_points: int
    damage_dealt: int
    damage_received: int
    shots: int
    xp: int
    survived_battles: int
    dropped_capture_points: int
    
    winrate: float
    avg_damage: int
    battles: int
    accuracy: float
    damage_ratio: float
    destruction_ratio: float
    frags_per_battle: float
    survival_ratio: float
    avg_spotted: float


class MainSession(BaseModel):
    hits: int
    frags: int
    wins: int
    losses: int
    capture_points: int
    damage_dealt: int
    damage_received: int
    shots: int
    xp: int
    survived_battles: int
    dropped_capture_points: int
    
    winrate: float
    avg_damage: int
    battles: int
    accuracy: float
    damage_ratio: float
    destruction_ratio: float
    frags_per_battle: float
    survival_ratio: float
    avg_spotted: float


class RatingDiff(BaseModel):
    winrate: float
    rating: int
    battles: int


class RatingSession(BaseModel):
    winrate: float
    rating: int
    battles: int
    

class SessionDiffData(BaseModel):
    main_diff: MainDiff
    main_session: MainSession
    rating_diff: RatingDiff
    rating_session: RatingSession
    tank_stats: dict[str, TankSessionData]