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


app = FastAPI()

class Server:
    def __init__(self):
        self.app = app
        self.app.mount('/register_success', asgi_app(self.pywebio_page))

    def pywebio_page(self):
        put_markdown('# 🎉 Registration is complete, you can close the page 🎉')
        put_info(f'authorized as: {_current_user["username"]}', closable=True)

    @app.get('/')
    async def root():
        return 
    
    @app.get(
        '/ping', 
        responses={
            501: {'model' : ErrorResponse, 'description' : 'Acces denied'},
            200: {'model' : InfoResponse, 'description' : 'Pong!'}
        }
    )
    async def ping(api_key: str):
        if api_key != _config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.acces_denied.model_dump(), status_code=501)
        
        return InfoResponses.pong

    @app.get('/api')
    async def api(response = Response) -> ErrorResponse:
        response.status_code = 500
        return ErrorResponses.method_not_allowed
    
    @app.get('/api/restart_session')
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
    
    @app.get('/api/get_player')
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
    
    @app.post('/api/set_player') 
    async def set_player(api_key: str, player: DBPlayer, response = Response) -> ErrorResponse | InfoResponse:
        if api_key != _config.INTERNAL_API_KEY:
            response.status_code = 501
            return ErrorResponses.acces_denied
        
        if _pdb.check_member(player.id):
            return JSONResponse(ErrorResponses.player_not_found.model_dump(), status_code=502)
        
        _pdb.set_member(player.id, player.nickname, player.region, player)
        _log.info(f'Player {player.nickname} : {player.id} updated')
        return InfoResponses.player_updated


if __name__ == '__main__':
    uvicorn.run(Server().app, host='127.0.0.1', port=8000)