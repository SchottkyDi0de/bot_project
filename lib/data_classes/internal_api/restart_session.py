from pydantic import BaseModel

from lib.settings.settings import Config
from lib.data_classes.db_player import SessionSettings

_config = Config().get()


class RestartSession(BaseModel):
    discord_id: int
    
class SessionState(BaseModel):
    active_session: bool
    session_ttl: int = _config.session.ttl
    autosession_ttl: int = _config.autosession.ttl
    session_settings: SessionSettings