from python_easy_json import JSONObject


class All(JSONObject):
    spotted: int = None
    hits: int = None
    frags: int = None
    max_xp: int = None
    wins: int = None
    losses: int = None
    capture_points: int = None
    battles: int = None
    damage_dealt: int = None
    damage_received: int = None
    max_frags: int = None
    shoots: int = None
    frags8p: int = None
    xp: int = None
    win_and_survived: int = None
    survived_battles: int = None
    dropped_capture_points: int = None

    winrate: float = None
    avg_damage: float = None


class TankStats(JSONObject):
    all: All = None
    last_battle_time: int = None
    account_id: int = None
    max_xp: int = None
    in_garage_updated: int = None
    max_frags: int = None
    frags: int | bool = None
    mark_of_mastery: int = None
    battle_life_time: int = None
    in_garage: bool = None
    tank_id: int = None
