from pydantic import BaseModel


class ServerSettings(BaseModel):
    allow_custom_backgrounds: bool = True
    
    
def set_server_settings(**kwargs) -> ServerSettings:
    '''
    Setup server settings from kwargs
    If value is None, it will be ignored
    '''
    return ServerSettings(**{k: v for k, v in kwargs.items() if v is not None})
    
    
class DBServer(BaseModel):
    _id: object | None = None
    id: int
    name: str
    settings: ServerSettings | None
    premium: bool = False
    custom_background: str | None = None
    work_channels: list[int] = []
