import traceback

import fastapi
import pywebio
from pywebio.input import *
from pywebio.output import *
from fastapi.responses import JSONResponse
from aiohttp import ClientSession

from lib.api.async_discord_api import DiscordApi
from lib.auth.dicord import DiscordOAuth

class AuthServer:
    def __init__(self) -> None:
        self.app = fastapi.FastAPI()
        
        self.ds_api = DiscordApi()
        self.ds_oauth = DiscordOAuth()
        self.app.add_api_route('/', self.root)
        self.app.add_api_route('/auth/discord', self.discord_auth)
        self.app.add_api_route('/auth/game', self.game_auth)
    
    async def root(self):
        return
    
    async def discord_auth(self):
        pass
    
    async def game_auth(self):
        pass
    