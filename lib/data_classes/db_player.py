from typing import Any

from pydantic import BaseModel


class ImageSettings(BaseModel):
    use_custom_bg: bool = True
    blocks_bg_brightness: float = 0.5
    glass_effect: int = 5
    nickname_color: str = '#f0f0f0' # Hex RGB Format #RRGGBB or #RGB
    clan_tag_color: str = '#0088fc' # Hex validator: lib.image.utils.hex_color_validator
    stats_color: str = '#f0f0f0'
    main_text_color: str = '#0088fc'
    stats_text_color: str = '#0088fc'
    disable_flag: bool = False
    hide_nickname: bool = False
    hide_clan_tag: bool = False
    disable_stats_blocks: bool = False
    disable_rating_stats: bool = False


def set_image_settings(**kwargs) -> ImageSettings:
    '''
    Setup image settings from kwargs
    If value is None, it will be ignored
    '''
    return ImageSettings(**{k: v for k, v in kwargs.items() if v is not None})


class DBPlayer(BaseModel):
    _id: object | None = None
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
    image_settings: ImageSettings | None = None
