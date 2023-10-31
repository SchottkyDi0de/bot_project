from python_easy_json import JSONObject


class Meta(JSONObject):
    count: int = None


class Rating(JSONObject):
    spotted: int = None
    calibration_battles_left: int = None
    hits: int = None
    frags: int = None
    recalibration_start_time: int = None
    mm_rating: float = None
    wins: int = None
    losses: int = None
    is_recalibration: bool = None
    capture_points: bool = None
    capture_points: int = None
    battles: int = None
    current_season: int = None
    damage_dealt: int = None
    damage_recieved: int = None
    shots: int = None
    frags8p: int = None
    xp: int = None
    win_and_survived: int = None
    survived_battles: int = None
    dropped_capture_points: int = None
    max_xp: int = None
    max_xp_tanx_id: int = None

    rating: int = None
    winrate: float = None


class All(JSONObject):
    spotted: int = None
    max_frags_tank_id: int = None
    hits: int = None
    max_frags: int = None
    frags: int = None
    wins: int = None
    losses: int = None
    capture_points: int = None
    battles: int = None
    damage_dealt: int = None
    damage_received: int = None
    shots: int = None
    frags8p: int = None
    xp: int = None
    win_and_survived: int = None
    survived_battles: int = None
    dropped_capture_points: int = None
    max_xp: int = None
    max_xp_tanx_id: int = None

    avg_xp: int = None
    avg_damage: int = None
    accuracy: float = None
    winrate: float = None
    avg_spotted: int = None
    frags_per_battle: int = None
    not_survived_battles: int = None
    survival_ratio: float = None
    damage_ratio: float = None
    destruction_ratio: float = None


class Statistics(JSONObject):
    rating: Rating = None
    all: All = None


class PlayerData(JSONObject):
    statistics: Statistics = None
    nickname: str = None
    account_id: int = None
    created_at: int = None
    updated_at: int = None
    private: bool = None
    last_battle_time: int = None


class PlayerStats(JSONObject):
    status: str = None
    meta: Meta = None
    data: PlayerData = None
