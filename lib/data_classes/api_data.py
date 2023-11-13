from typing import List, Optional

from pydantic import BaseModel

from lib.data_classes.palyer_clan_stats import Clan
from lib.data_classes.player_achievements import Achievements
from lib.data_classes.player_stats import Statistics
from lib.data_classes.tanks_stats import TankStats


class Player(BaseModel):
    achievements: Achievements
    clan_stats: Clan
    tank_stats: List[TankStats]
    statistics: Statistics
    name_and_tag: Optional[str] = None
    clan_tag: Optional[str]


class PlayerGlobalData(BaseModel):
    id: int
    data: Player
    region: str
    lower_nickname: str
    timestamp: int
    end_timestamp: int
    nickname: str
    from_cache: Optional[bool] = False
