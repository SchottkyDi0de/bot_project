from python_easy_json import JSONObject
from typing import List


class Author(JSONObject):
    hitpoints_left: int
    total_credits: int
    total_xp: int
    n_shots: int
    n_hits: int
    n_splashes: int
    n_penetraions: int
    damage_dealt: int
    account_id: int
    team_number: int


class AvatarInfo(JSONObject):
    gfx_url: str
    gfx2_url: str
    kind: str


class Avatar(JSONObject):
    info: AvatarInfo


class PlayerInfo(JSONObject):
    nickname: str
    platoon_id: int
    team: int
    clan_tag: str | None
    avatar: Avatar


class Player(JSONObject):
    account_id: int
    info: PlayerInfo


class PlayerResultInfo(JSONObject):
    credits_earned: int
    base_xp: int
    n_shots: int
    n_hits_dealt: int
    n_penetraions: int
    damage_dealt: int
    damage_assisted_1: int
    damage_assisted_2: int
    h_hits_recivied: int
    n_non_penetrating_hits: int
    n_enemies_damaged: int
    n_enemies_destroyed: int
    victory_points_earned: int
    victory_points_seized: int
    account_id: int
    mm_rating: int
    damage_blocked: int


class PlayerResult(JSONObject):
    result_id: int
    info: PlayerResultInfo


class CommonReplayData(JSONObject):
    mode_map_id: int
    timestamp_secs: int
    winner_team_number: int
    author: Author
    room_type: str
    free_xp: int
    players: List[Player]
    player_results: List[PlayerResult]
