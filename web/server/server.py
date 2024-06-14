import traceback
from typing import Annotated

from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from lib.data_classes.db_player import DBPlayer
from lib.data_classes.internal_api.err_response import ErrorResponse
from lib.data_classes.internal_api.inf_response import InfoResponse
from lib.database.players import PlayersDB
from lib.data_classes.internal_api.restart_session import SessionState
from lib.internal_api.responses import ErrorResponses, InfoResponses
from lib.logger.logger import get_logger
from lib.settings.settings import EnvConfig
from web.components import session_widget
from web.components import auth
from lib.database.internal import InternalDB

_pdb = PlayersDB()
_env_config = EnvConfig()
_log = get_logger(__file__, 'ServerLogger', 'logs/server.log')


app = FastAPI(docs_url='/bot/api/docs')

class AllUsers(BaseModel):
    count: int

class PremiumUsers(BaseModel):
    data: list[int]

class AllSessions(BaseModel):
    count: int


class Server:
    
    @app.get('/', include_in_schema=False)
    async def root():
        return None

    @app.get('/bot', include_in_schema=False)
    async def bot_root():
        return None
    
    @app.get('/bot/api/ping',
        responses={
            418: {'model' : ErrorResponse, 'description' : 'Access denied'},
            200: {'model' : InfoResponse, 'description' : 'Pong!'}
        }
    )
    async def ping(api_key: Annotated[str, Header()]):
        if api_key != _env_config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
        
        return InfoResponses.pong
        
    @app.get('/bot/api', include_in_schema=False)
    def api_root(self):
        pass
 
    @app.get('/bot/api/get_all_users', responses={
        418: {'model' : ErrorResponse, 'description' : 'Access denied'},
        200: {'model' : AllUsers, 'description' : 'All users'}    
        }
    )
    async def get_all_users(api_key: Annotated[str, Header()]) -> AllUsers | ErrorResponse:
        if api_key != _env_config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
        
        users = await _pdb.get_all_members_count()
        return JSONResponse({'count' : users}, status_code=200)

    @app.get('/bot/api/get_all_sessions', responses={
        418: {'model' : ErrorResponse, 'description' : 'Access denied'},
        200: {'model' : AllSessions, 'description' : 'All sessions'}
        }
    )
    async def get_all_sessions(api_key: Annotated[str, Header()]) -> AllSessions | ErrorResponse:
        if api_key != _env_config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
        
        sessions = await _pdb.count_sessions()
        return JSONResponse({'count' : sessions}, status_code=200)
    
    @app.post('/bot/api/update_server_members', responses={
        418: {'model' : ErrorResponse, 'description' : 'Access denied'},
        200: {'model' : InfoResponse, 'description' : 'Members updated'}
        }
    )
    async def update_server_members(api_key: Annotated[str, Header()], premium_users: PremiumUsers) -> InfoResponse | ErrorResponse:
        if api_key != _env_config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
        
        await InternalDB().set_actual_premium_users(premium_users.data)
        return JSONResponse(InfoResponses.set_ok.model_dump(), status_code=200)
    
def run():
    session_widget.init_app(app)
    auth.init_app(app)
    return app

if __name__ == '__main__':
    print('Server cannot be run directly, use run_server.py script instead')