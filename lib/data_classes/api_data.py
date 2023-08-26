from typing import List

from python_easy_json import JSONObject

from lib.data_classes.palyer_clan_stats import ClanStats
from lib.data_classes.player_achievements import Achievements
from lib.data_classes.player_stats import Statistics
from lib.data_classes.tanks_stats import TankStats


class Player(JSONObject):
    achievements: Achievements = None
    clan_stats: ClanStats = None
    tank_stats: List[TankStats]
    statistics: Statistics = None
    name_and_tag: str = None
    clan_tag: str = None


class PlayerGlobalData(JSONObject):
    id: int = None
    data: Player = None
    region: str = None
    lower_nickname: str = None
    timestamp: int = None
    nickname: str = None
