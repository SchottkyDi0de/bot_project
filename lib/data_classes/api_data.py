from typing import List

from python_easy_json import JSONObject

from lib.data_classes.palyer_clan_stats import Clan
from lib.data_classes.player_achievements import Achievements
from lib.data_classes.player_stats import Statistics
from lib.data_classes.tanks_stats import TankStats


class Player(JSONObject):
    achievements: Achievements = Achievements()
    clan_stats: Clan = Clan()
    tank_stats: List[TankStats]
    statistics: Statistics = Statistics()
    name_and_tag: str = None
    clan_tag: str = None


class PlayerGlobalData(JSONObject):
    id: int = None
    data: Player = Player()
    region: str = None
    lower_nickname: str = None
    timestamp: int = None
    nickname: str = None
