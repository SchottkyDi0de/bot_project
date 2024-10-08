from typing import Any
from datetime import datetime

import pytz
from pydantic import BaseModel


class StatsViewSettings(BaseModel):
    common_slots: dict = {
        'slot_1' : 'winrate',
        'slot_2' : 'avg_damage',
        'slot_3' : 'battles',
        'slot_4' : 'accuracy'
    }
    rating_slots: dict = {
        'slot_1' : 'winrate',
        'slot_2' : 'avg_damage',
        'slot_3' : 'battles',
        'slot_4' : 'rating'
    }

class WidgetSettings(BaseModel):
    disable_bg: bool = False
    disable_nickname: bool = False
    max_stats_blocks: int = 1
    max_stats_small_blocks: int = 0
    update_time: int = 30  # Seconds
    background_transparency: float = 0.25
    disable_main_stats_block: bool = False
    use_bg_for_stats_blocks: bool = True
    adaptive_width: bool = False
    stats_block_color: str = '#bababa'

class SessionSettings(BaseModel):
    is_autosession: bool = False
    last_get: datetime = datetime.now(pytz.utc)  # UTC Time of last session get (Date object)
    timezone: int = 0  # Hours add to UTC (Simple timezone represent)
    time_to_restart: datetime = datetime.now(pytz.utc).replace(hour=0, minute=0, second=0) # Date object
    stats_view: StatsViewSettings = StatsViewSettings()

class ImageSettings(BaseModel):
    theme: str = 'default'
    colorize_stats: bool = True
    use_custom_bg: bool = True
    hide_nickname: bool = False
    hide_clan_tag: bool = False
    disable_flag: bool = False
    disable_rating_stats: bool = False
    disable_cache_label: bool = False
    disable_stats_blocks: bool = False
    stats_blocks_transparency: float = 0.5
    glass_effect: int = 5
    nickname_color: str = '#f0f0f0' # Hex RGB Format #RRGGBB or #RGB
    clan_tag_color: str = '#0088fc' # Hex validator: lib.image.utils.hex_color_validator
    stats_color: str = '#f0f0f0'
    main_text_color: str = '#0088fc'
    stats_text_color: str = '#0088fc'
    negative_stats_color: str = '#c01515'
    positive_stats_color: str = '#1eff26'

class DBPlayerOld(BaseModel):
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