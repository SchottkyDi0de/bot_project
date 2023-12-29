import traceback
from typing import Union, Annotated

from fastapi import FastAPI, Response, Header
from fastapi.responses import JSONResponse, RedirectResponse
from pywebio.input import *
from pywebio.output import *
from pywebio.platform.fastapi import asgi_app
import uvicorn

from lib.api.async_wotb_api import API
from lib.data_classes.db_player import DBPlayer
from lib.data_classes.internal_api.err_response import ErrorResponse
from lib.data_classes.internal_api.inf_response import InfoResponse
from lib.database.players import PlayersDB
from lib.data_classes.internal_api.restart_session import RestartSession
from lib.internal_api.responses import ErrorResponses, InfoResponses
from lib.logger.logger import get_logger
from lib.settings.settings import Config, EnvConfig

_current_user = None
_pdb = PlayersDB()
_config = EnvConfig()
_api = API()

_log = get_logger(__name__, 'ServerLogger', 'logs/server.log')

app = FastAPI(docs_url='/bot/api/docs')


class Server:
    def __init__(self):
        self.app = app
        self.app.mount('/register_success', asgi_app(self.pywebio_page))

    def pywebio_page(self):
        put_markdown('# 🎉 Registration is complete, you can close the page 🎉')
        put_info(f'authorized as: {_current_user["username"]}', closable=True)

    @app.get('/', include_in_schema=False)
    async def root():
        return
    
    @app.get('/bot/api/ping', 
        responses={
            501: {'model' : ErrorResponse, 'description' : 'Acces denied'},
            200: {'model' : InfoResponse, 'description' : 'Pong!'}
        }
    )
    async def ping(api_key: Annotated[str, Header()]):
        if api_key != _config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.acces_denied.model_dump(), status_code=501)
        
        return InfoResponses.pong

    @app.get('/bot/api', responses={
        500: {'model' : ErrorResponse, 'description' : 'Root method not allowed'},
        }
    )
    async def api(response = Response) -> ErrorResponse:
        return JSONResponse(ErrorResponses.method_not_allowed.model_dump(), status_code=500)
    
    @app.post('/bot/api/restart_session', responses={
        501: {'model' : ErrorResponse, 'description' : 'Acces denied'},
        502: {'model' : ErrorResponse, 'description' : 'Player not found'},
        504: {'model' : ErrorResponse, 'description' : 'Player session not found'},
        200: {'model' : InfoResponse, 'description' : 'Player updated'},
        }
    )
    async def restart_session(api_key: Annotated[str, Header()], data: RestartSession) -> ErrorResponse:
        if api_key != _config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.acces_denied.model_dump(), status_code=501)
        
        if _pdb.check_member(data.discord_id):
            if _pdb.check_member_last_stats(data.discord_id):
                player = _pdb.get_member(data.discord_id)
                
                if player is None:
                    return JSONResponse(ErrorResponses.player_not_found.model_dump(), status_code=502)
                
                player_data = await _api.get_stats(player['nickname'], player['region'])
                _pdb.set_member_last_stats(data.discord_id, player_data.model_dump())
                return JSONResponse(InfoResponses.player_updated.model_dump(), status_code=200)
            
            return JSONResponse(ErrorResponses.player_session_not_found.model_dump(), status_code=504)
        return JSONResponse(ErrorResponses.player_not_found.model_dump(), status_code=502)
    
    @app.get('/bot/api/get_player', responses={
        501: {'model' : ErrorResponse, 'description' : 'Acces denied'},
        502: {'model' : ErrorResponse, 'description' : 'Player not found'},
        200: {'model' : DBPlayer, 'description' : 'Player data'}
        }
    )
    async def get_player(api_key: Annotated[str, Header()], discord_id: str | int, include_traceback: bool = False) -> DBPlayer | ErrorResponse:
        if api_key != _config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.acces_denied.model_dump(), status_code=501)
        
        player = _pdb.get_member(discord_id)

        if player is not None:
            try:
                player = DBPlayer.model_validate(player)
                player.last_stats = None
                return JSONResponse(player.model_dump(), status_code=200)
            
            except:
                _log.error(traceback.format_exc())
                err_response = ErrorResponses.validation_error
                if include_traceback:
                    err_response.traceback = traceback.format_exc()
                    
                return JSONResponse(err_response.model_dump(), status_code=503)
                
        else:
            err_response = ErrorResponses.player_not_found
            if include_traceback:
                err_response.traceback = traceback.format_exc()
                
            return JSONResponse(err_response.model_dump(), status_code=502)
    
    @app.post('/bot/api/set_player', responses={
        501: {'model' : ErrorResponse, 'description' : 'Acces denied'},
        502: {'model' : ErrorResponse, 'description' : 'Player not found'},
        200: {'model' : InfoResponse, 'description' : 'Player updated'}
        }
    ) 
    async def set_player(api_key: Annotated[str, Header()], player: DBPlayer) -> ErrorResponse | InfoResponse:
        if api_key != _config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.acces_denied.model_dump(), status_code=501)
        
        if _pdb.check_member(player.id):
            return JSONResponse(ErrorResponses.player_not_found.model_dump(), status_code=502)
        
        _pdb.safe_update_member(player.id, player)
        _log.info(f'Player {player.nickname} : {player.id} updated')
        return JSONResponse(InfoResponses.player_updated.model_dump(), status_code=200)


if __name__ == '__main__':
    uvicorn.run(Server().app, host='127.0.0.1', port=8000)