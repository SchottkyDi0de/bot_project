from pydantic import BaseModel


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
    

class SesionDiffData(BaseModel):
    main_diff: MainDiff
    main_session: MainSession
    rating_diff: RatingDiff
    rating_session: RatingSession
    tank_diff: TankDiff
    tank_session: TankSession
    tank_id: int
    tank_index: int