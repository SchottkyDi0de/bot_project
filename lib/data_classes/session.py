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
    hits: int = 0
    frags: int = 0
    wins: int = 0
    losses: int = 0
    capture_points: int = 0
    damage_dealt: int = 0
    damage_received: int = 0
    shots: int = 0
    xp: int = 0
    survived_battles: int = 0
    dropped_capture_points: int = 0
    
    winrate: float = 0.0
    avg_damage: int = 0
    battles: int = 0
    accuracy: float = 0.0
    damage_ratio: float = 0.0
    destruction_ratio: float = 0.0
    frags_per_battle: float = 0.0
    survival_ratio: float = 0.0
    avg_spotted: float = 0.0


class MainSession(BaseModel):
    hits: int = 0
    frags: int = 0
    wins: int = 0
    losses: int = 0
    capture_points: int = 0
    damage_dealt: int = 0
    damage_received: int = 0
    shots: int = 0
    xp: int = 0
    survived_battles: int = 0
    dropped_capture_points: int = 0
    
    winrate: float = 0.0
    avg_damage: int = 0
    battles: int = 0
    accuracy: float = 0.0
    damage_ratio: float = 0.0
    destruction_ratio: float = 0.0
    frags_per_battle: float = 0.0
    survival_ratio: float = 0.0
    avg_spotted: float = 0.0


class RatingDiff(BaseModel):
    winrate: float = 0.0
    rating: int = 0
    battles: int = 0


class RatingSession(BaseModel):
    winrate: float = 0.0
    rating: int = 0
    battles: int = 0
    

class SessionDiffData(BaseModel):
    main_diff: MainDiff
    main_session: MainSession
    rating_diff: RatingDiff
    rating_session: RatingSession
    tank_stats: dict[str, TankSessionData] | None