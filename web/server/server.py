import traceback
from typing import Annotated

from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pywebio.output import *

from lib.data_classes.db_player import DBPlayer, ImageSettings
from lib.data_classes.internal_api.err_response import ErrorResponse
from lib.data_classes.internal_api.inf_response import InfoResponse
from lib.database.players import PlayersDB
from lib.data_classes.internal_api.restart_session import SessionState
from lib.internal_api.responses import ErrorResponses, InfoResponses
from lib.logger.logger import get_logger
from lib.settings.settings import EnvConfig
from web.components import session_widget
from web.components import auth

_pdb = PlayersDB()
_env_config = EnvConfig()
_log = get_logger(__file__, 'ServerLogger', 'logs/server.log')


app = FastAPI(docs_url='/bot/api/docs')

class AllUsers(BaseModel):
    count: int


class AllSessions(BaseModel):
    count: int


class Server:
    
    @app.get('/', include_in_schema=False)
    async def root():
        return None

    @app.get('/bot', include_in_schema=False)
    async def root():
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
    def root(self):
        pass
    
    @app.get('/bot/api/session_state', responses = {
        418: {'model' : ErrorResponse, 'description' : 'Access denied'},
        400: {'model' : ErrorResponse, 'description' : 'Player not found'},
        200: {'model' : InfoResponse, 'description' : 'Data sent successfully'},
        }
    )
    async def session_state(api_key: Annotated[str, Header()], discord_id: int | str):
        if api_key != _env_config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
        
        if _pdb.check_member(discord_id):
            active_session = _pdb.check_member_last_stats(discord_id)
            state = SessionState.model_validate(
                {
                    'active_session' : active_session,
                    'session_settings' : _pdb.get_member_session_settings(discord_id)
                }
            )
            return JSONResponse(state.model_dump(), status_code=200)
        
        return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
    
    @app.get('/bot/api/get_player', responses={
        418: {'model' : ErrorResponse, 'description' : 'Access denied'},
        400: {'model' : ErrorResponse, 'description' : 'Player not found'},
        200: {'model' : DBPlayer, 'description' : 'Player data'}
        }
    )
    async def get_player(
            api_key: Annotated[str, Header()], 
            discord_id: str | int, 
            include_image: bool = False,
            include_session: bool = False,
            include_traceback: bool = False
        ) -> DBPlayer | ErrorResponse:
        
        if api_key != _env_config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
        
        player = _pdb.get_member(discord_id)

        if player is not None:
            try:
                player = DBPlayer.model_validate(player)
                
                if not include_image:
                    player.image = None
                if not include_session:
                    player.last_stats = None
                
                return JSONResponse(player.model_dump(), status_code=200)
            
            except:
                _log.error(traceback.format_exc())
                err_response = ErrorResponses.validation_error
                if include_traceback:
                    err_response.traceback = traceback.format_exc()
                    
                return JSONResponse(err_response.model_dump(), status_code=err_response.code)
                
        else:
            err_response = ErrorResponses.player_not_found
            if include_traceback:
                err_response.traceback = traceback.format_exc()
                
            return JSONResponse(err_response.model_dump(), status_code=err_response.code)

    @app.get('/bot/api/get_image_settings', responses={
        418: {'model' : ErrorResponse, 'description' : 'Access denied'},
        400: {'model' : ErrorResponse, 'description' : 'Player not found'},
        200: {'model' : ImageSettings, 'description' : 'Image settings'}
        }
    )
    async def get_image_settings(api_key: Annotated[str, Header()], discord_id: str | int) -> ImageSettings | ErrorResponse:
        if api_key != _env_config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
        
        if _pdb.check_member(discord_id):
            image_settings = _pdb.get_image_settings(discord_id)
            return JSONResponse(image_settings.model_dump(), status_code=200)
        
        else:
            err_response = ErrorResponses.player_not_found
            return JSONResponse(err_response.model_dump(), status_code=err_response.code)
        
    @app.post('/bot/api/set_image_settings', responses={
        418: {'model' : ErrorResponse, 'description' : 'Access denied'},
        400: {'model' : ErrorResponse, 'description' : 'Player not found'},
        200: {'model' : InfoResponse, 'description' : 'Image settings updated'}
        }
    )
    async def set_image_settings(api_key: Annotated[str, Header()], discord_id: str | int, image_settings: ImageSettings) -> InfoResponse | ErrorResponse:
        if api_key != _env_config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
        
        if _pdb.check_member(discord_id):
            image_settings = _pdb.set_image_settings(discord_id, image_settings)
            return JSONResponse(InfoResponses.image_settings_updated.model_dump(), status_code=200)
        
        else:
            err_response = ErrorResponses.player_not_found
            return JSONResponse(err_response.model_dump(), status_code=err_response.code)
        
    @app.get('/bot/api/get_all_users', responses={
        418: {'model' : ErrorResponse, 'description' : 'Access denied'},
        200: {'model' : AllUsers, 'description' : 'All users'}    
        }
    )
    async def get_all_users(api_key: Annotated[str, Header()]) -> AllUsers | ErrorResponse:
        if api_key != _env_config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
        
        users = _pdb.count_members()
        return JSONResponse({'count' : users}, status_code=200)

    @app.get('/bot/api/get_all_sessions', responses={
        418: {'model' : ErrorResponse, 'description' : 'Access denied'},
        200: {'model' : AllSessions, 'description' : 'All sessions'}
        }
    )
    async def get_all_sessions(api_key: Annotated[str, Header()]) -> AllSessions | ErrorResponse:
        if api_key != _env_config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
        
        sessions = _pdb.count_sessions()
        return JSONResponse({'count' : sessions}, status_code=200)

    
def run():
    session_widget.init_app(app)
    auth.init_app(app)
    return app

if __name__ == '__main__':
    print('Server cannot be run directly, use run_server.py script instead')