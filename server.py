# from pywebio import start_server
import uvicorn
from pywebio.input import *
from pywebio.output import *
from pywebio.platform.fastapi import asgi_app
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from lib.api.aync_discord_api import DiscordApi
from lib.auth.dicord import DiscordOAuth
from lib.settings.settings import Config
from lib.database.players import PlayersDB
from lib.data_classes.db_player import DBPlayer

_current_user = None
_pdb = PlayersDB()
_config = Config()

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
    async def api():
        return
    
    @app.get('/api/get_player')
    async def get_player(api_key: str, discord_id: str | int) -> dict:
        if api_key != _config.INTERNAL_API_KEY:
            return {'Error': 'AccesDenied'}
        
        player = _pdb.get_member(discord_id)

        if player is not None:
            try:
                return DBPlayer.model_validate(player)
            except:
                return {'Error': 'DataValidationError'}
        else:
            return {'Error': 'PlayerNotFound'}
    
    @app.post('/api/set_player')
    async def set_player(api_key: str, player: DBPlayer):
        if api_key != _config.INTERNAL_API_KEY:
            return {'Error': 'AccesDenied'}
        
        _pdb.set_member(player.id, player.nickname, player.region, player)
        return {'Success': 'PlayerUpdated'}

    @app.get('/auth')
    async def auth(code: str):
        global _current_user
        token = await DiscordOAuth().exchange_code(code)
        _current_user = await DiscordApi().get_user_data(token)
        return RedirectResponse('/register_success')

if __name__ == '__main__':
    uvicorn.run(Server().app, host='0.0.0.0', port=8000)
