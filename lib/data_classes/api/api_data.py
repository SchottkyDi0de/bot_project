from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

from lib.data_classes.api.player_achievements import Achievements
from lib.data_classes.api.player_clan_stats import Clan
from lib.data_classes.api.player_stats import Statistics
from lib.data_classes.api.tanks_stats import TankStats


class Player(BaseModel):
    achievements: Achievements
    clan_stats: Optional[Clan] = None
    tank_stats: Dict[str, TankStats]
    statistics: Statistics
    name_and_tag: Optional[str] = None
    clan_tag: Optional[str]


class PlayerGlobalData(BaseModel):
    id: int
    data: Player
    region: str
    lower_nickname: str
    timestamp: datetime
    nickname: str
    from_cache: Optional[bool] = False
