from pydantic import BaseModel


class SessionImageGenExtraSettings(BaseModel):
    disable_bg: bool = False
    disable_tank_stats: bool = False
    stats_blocks_limit: int = 4
    stats_small_blocks_limit: int = 2
    stats_blocks_color: tuple[int, int, int, int] = (0, 0, 0, 80)
    

class CommonImageGenExtraSettings(BaseModel):
    hide_nickname: bool = False
    hide_clan_tag: bool = False
