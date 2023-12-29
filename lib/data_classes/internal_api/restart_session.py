from pydantic import BaseModel

class RestartSession(BaseModel):
    discord_id: int