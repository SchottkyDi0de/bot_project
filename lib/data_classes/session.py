from pydantic import BaseModel

class TankSessionData(BaseModel):
    tank_name: str
    tank_tier: int
    tank_type: str
    tank_id: int
    
    d_winrate: float
    d_avg_damage: int
    d_battles: int
    
    s_winrate: float
    s_avg_damage: int
    s_battles: int

class TankDiff(BaseModel):
    winrate: float = 0
    avg_damage: int
    battles: int


class TankSession(BaseModel):
    winrate: float
    avg_damage: int
    battles: int


class MainDiff(BaseModel):
    winrate: float
    avg_damage: int
    battles: int


class MainSession(BaseModel):
    winrate: float
    avg_damage: int
    battles: int


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