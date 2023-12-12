from typing import Optional, Any

from pydantic import BaseModel

class DBPlayer(BaseModel):
    id: int
    nickname: str
    region: str
    premium: Optional[bool]
    premium_time: Optional[int]
    lang: Optional[str]
    last_stats: Optional[dict[str, Any]] = None
    image: Optional[str] = None
    locked: bool = False
    verified: bool = False
    
class DBPlayerSetResponse(BaseModel):
    player_data: DBPlayer
    api_key: str