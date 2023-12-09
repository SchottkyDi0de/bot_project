import traceback
from typing import Union

from fastapi import FastAPI, Response
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
from lib.internal_api.responses import ErrorResponses, InfoResponses
from lib.logger.logger import get_logger
from lib.settings.settings import Config

_current_user = None
_pdb = PlayersDB()
_config = Config()
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
    
    @app.get(
        '/bot/api/ping', 
        responses={
            501: {'model' : ErrorResponse, 'description' : 'Acces denied'},
            200: {'model' : InfoResponse, 'description' : 'Pong!'}
        }
    )
    async def ping(api_key: str):
        if api_key != _config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.acces_denied.model_dump(), status_code=501)
        
        return InfoResponses.pong

    @app.get('/bot/api', responses={
        501: {'model' : ErrorResponse, 'description' : 'Root method not allowed'},
        }
    )
    async def api(response = Response) -> ErrorResponse:
        return JSONResponse(ErrorResponses.method_not_allowed.model_dump(), status_code=500)
    
    @app.get('/bot/api/restart_session', responses={
        501: {'model' : ErrorResponse, 'description' : 'Acces denied'},
        502: {'model' : ErrorResponse, 'description' : 'Player not found'},
        504: {'model' : ErrorResponse, 'description' : 'Player session not found'},
        200: {'model' : InfoResponse, 'description' : 'Player updated'}
        }
    )
    async def restart_session(api_key: str, discord_id: str | int) -> ErrorResponse:
        if api_key != _config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.acces_denied.model_dump(), status_code=501)
        
        if _pdb.check_member(discord_id):
            if _pdb.check_member_last_stats(discord_id):
                player = _pdb.get_member(discord_id)
                
                if player is None:
                    return JSONResponse(ErrorResponses.player_not_found.model_dump(), status_code=502)
                
                player_data = await _api.get_stats(player['nickname'], player['region'])
                _pdb.set_member_last_stats(discord_id, player_data.model_dump())
                return JSONResponse(InfoResponses.player_updated.model_dump(), status_code=200)
            
            return JSONResponse(ErrorResponses.player_session_not_found.model_dump(), status_code=504)
        return JSONResponse(ErrorResponses.player_not_found.model_dump(), status_code=502)
    
    @app.get('/bot/api/get_player', responses={
        501: {'model' : ErrorResponse, 'description' : 'Acces denied'},
        502: {'model' : ErrorResponse, 'description' : 'Player not found'},
        200: {'model' : DBPlayer, 'description' : 'Player data'}
        }
    )
    async def get_player(api_key: str, discord_id: str | int, include_traceback: bool = False, response = Response) -> DBPlayer | ErrorResponse:
        if api_key != _config.INTERNAL_API_KEY:
            response.status_code = 501
            return
        
        player = _pdb.get_member(discord_id)

        if player is not None:
            try:
                player = DBPlayer.model_validate(player)
                player.last_stats = None
                return player
            except:
                _log.error(traceback.format_exc())
                response.status_code = 503
                err_response = ErrorResponses.validation_error
                if include_traceback:
                    err_response.traceback = traceback.format_exc()
                    
                return err_response
                
        else:
            response.status_code = 502
            err_response = ErrorResponses.player_not_found
            if include_traceback:
                err_response.traceback = traceback.format_exc()
                
            return err_response
    
    @app.post('/bot/api/set_player', responses={
        501: {'model' : ErrorResponse, 'description' : 'Acces denied'},
        502: {'model' : ErrorResponse, 'description' : 'Player not found'},
        200: {'model' : InfoResponse, 'description' : 'Player updated'}
        }
    ) 
    async def set_player(api_key: str, player: DBPlayer) -> ErrorResponse | InfoResponse:
        if api_key != _config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.acces_denied.model_dump(), status_code=501)
        
        if _pdb.check_member(player.id):
            return JSONResponse(ErrorResponses.player_not_found.model_dump(), status_code=502)
        
        _pdb.safe_update_member(player.id, player)
        _log.info(f'Player {player.nickname} : {player.id} updated')
        return JSONResponse(InfoResponses.player_updated.model_dump(), status_code=200)


if __name__ == '__main__':
    uvicorn.run(Server().app, host='blitzhub.ru', port=8000)