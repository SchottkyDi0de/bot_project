# from pywebio import start_server
import traceback
import enum

import uvicorn
from pywebio.input import *
from pywebio.output import *
from pywebio.platform.fastapi import asgi_app
from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse

from lib.api.aync_discord_api import DiscordApi
from lib.data_classes.internal_api.err_response import ErrorResponse
from lib.data_classes.internal_api.inf_response import InfoResponse
from lib.auth.dicord import DiscordOAuth
from lib.settings.settings import Config
from lib.database.players import PlayersDB
from lib.data_classes.db_player import DBPlayer
from lib.logger.logger import get_logger

_current_user = None
_pdb = PlayersDB()
_config = Config()

_log = get_logger(__name__, 'ServerLogger', 'logs/server.log')

class InfoResponses:
    succes = InfoResponse.model_validate(
        {   
            'info' : 'Success',
            'message': 'Player data has ben updated',
            'code': 200
        }
    )

class ErrorResponses:
    method_not_allowed =  ErrorResponse.model_validate(
        {
            'error': 'MethodNotAllowed', 
            'message': 'Root method of API not allowed',
            'code': 500
        }
    )
    acces_denied =  ErrorResponse.model_validate(
        {
            'error': 'AccesDenied', 
            'message': 'Invalid API KEY, acces denied',
            'code': 501
        }
    )
    player_not_found = ErrorResponse.model_validate(
        {
            'error': 'PlayerNotFound', 
            'message': 'Player not found in DB',
            'code': 502
        }
    )
    validation_error = ErrorResponse.model_validate(
        {
            'error': 'ValidationError', 
            'message': 'Error while validating data [INTERNAL ERROR]',
            'code': 503
        }
    )

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

    @app.get('/api')
    async def api(response = Response) -> ErrorResponse:
        response.status_code = 500
        return ErrorResponses.method_not_allowed
    
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
        
        _pdb.set_member(player.id, player.nickname, player.region, player)
        _log.info(f'Player {player.nickname} : {player.id} updated')
        return InfoResponses.succes

    @app.get('/auth')
    async def auth(code: str):
        global _current_user
        token = await DiscordOAuth().exchange_code(code)
        _current_user = await DiscordApi().get_user_data(token)
        return RedirectResponse('/register_success')

if __name__ == '__main__':
    uvicorn.run(Server().app, host='127.0.0.1', port=8000)

