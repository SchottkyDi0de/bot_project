from datetime import datetime
from typing import Any

import pytz
from pydantic import BaseModel


class StatsViewSettings(BaseModel):
    slots: dict = {
        'slot_1' : 'winrate',
        'slot_2' : 'avg_damage',
        'slot_3' : 'battles',
        'slot_4' : 'accuracy'
    }

class WidgetSettings(BaseModel):
    disable_bg: bool = True
    disable_nickname: bool = False
    max_stats_blocks: int = 3
    max_stats_small_blocks: int = 2
    update_per_seconds: int = 60  # Seconds
    stats_blocks_transparency: float = 0.7
    disable_main_stats_block: bool = False
    use_bg_for_stats_blocks: bool = False
    adaptive_width: bool = True
    stats_block_color: str = '#000000'

class SessionSettings(BaseModel):
    is_autosession: bool = False
    last_get: datetime = datetime.now(pytz.utc)  # UTC Time of last session get (Date object)
    timezone: int = 0  # Hours add to UTC (Simple timezone represent)
    time_to_restart: datetime = datetime.now(pytz.utc).replace(hour=0, minute=0, second=0) # Date object
    stats_view: StatsViewSettings = StatsViewSettings()

class ImageSettings(BaseModel):
    use_custom_bg: bool = True
    hide_nickname: bool = False
    hide_clan_tag: bool = False
    disable_flag: bool = False
    disable_rating_stats: bool = False
    disable_cache_label: bool = False
    disable_stats_blocks: bool = False
    blocks_bg_opacity: float = 0.5
    glass_effect: int = 5
    nickname_color: str = '#f0f0f0' # Hex RGB Format #RRGGBB or #RGB
    clan_tag_color: str = '#0088fc' # Hex validator: lib.image.utils.hex_color_validator
    stats_color: str = '#f0f0f0'
    main_text_color: str = '#0088fc'
    stats_text_color: str = '#0088fc'
    negative_stats_color: str = '#c01515'
    positive_stats_color: str = '#1eff26'
    
    
def set_widget_settings(**kwargs) -> WidgetSettings:
    '''
    Setup widget settings from kwargs
    If value is None, it will be ignored
    '''
    return WidgetSettings(**{k: v for k, v in kwargs.items() if v is not None})
    

def set_image_settings(**kwargs) -> ImageSettings:
    '''
    Setup image settings from kwargs
    If value is None, it will be ignored
    '''
    return ImageSettings(**{k: v for k, v in kwargs.items() if v is not None})


class DBPlayer(BaseModel):
    _id: Any | None = None
    id: int
    game_id: int
    nickname: str
    region: str
    premium: bool | None = None
    premium_time: int | None = None
    lang: str | None = None
    last_stats: dict[str, Any] | None = None
    image: str | None = None
    locked: bool = False
    verified: bool = False
    image_settings: ImageSettings = ImageSettings()
    session_settings: SessionSettings = SessionSettings()
    widget_settings: WidgetSettings = WidgetSettings()
