from python_easy_json import JSONObject


class TankDiff(JSONObject):
    winrate: float = None
    avg_damage: int = None
    battles: int = None

class TankSession(JSONObject):
    winrate: float = None
    avg_damage: int = None
    battles: int = None

class MainDiff(JSONObject):
    winrate: float = None
    avg_damage: int = None
    battles: int = None

class MainSession(JSONObject):
    winrate: float = None
    avg_damage: int = None
    battles: int = None

class RatingDiff(JSONObject):
    winrate: float = None
    rating: int = None
    battles: int = None

class RatingSession(JSONObject):
    winrate: float = None
    rating: int = None
    battles: int = None

class SesionDiffData(JSONObject):
    main_diff: MainDiff = None
    main_session: MainSession = None
    rating_diff: RatingDiff = None
    rating_session: RatingSession = None
    tank_diff: TankDiff = None
    tank_session: TankSession = None
    tank_id: int = None
    tenk_index: int = None
