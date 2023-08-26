from python_easy_json import JSONObject


class Tank(JSONObject):
    winrate: float = None
    avg_damage: int = None
    battles: int = None

class Main(JSONObject):
    winrate: float = None
    avg_damage: int = None
    battles: int = None

class Rating(JSONObject):
    winrate: float = None
    rating: int = None
    battles: int = None

class SesionDiffData(JSONObject):
    main: Main = None
    rating: Rating = None
    tank: Tank = None
    tank_id: int = None
    tenk_index: int = None
