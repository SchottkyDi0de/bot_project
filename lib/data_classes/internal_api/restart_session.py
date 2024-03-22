from pydantic import BaseModel

from lib.data_classes.db_player import SessionSettings
from lib.settings.settings import Config

_config = Config().get()


class RestartSession(BaseModel):
    discord_id: int
    
class SessionState(BaseModel):
    active_session: bool
    session_ttl: int = _config.session.ttl
    autosession_ttl: int = _config.autosession.ttl
    session_settings: SessionSettings