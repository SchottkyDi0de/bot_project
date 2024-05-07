from typing import Optional
from asyncio import sleep

from fastapi import Cookie, FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from nicegui import ui, Client

from lib.api.async_discord_api import DiscordApi
from lib.api.async_wotb_api import API
from lib.auth.discord import DiscordOAuth
from lib.data_classes.db_player import DBPlayer
from lib.database.players import PlayersDB
from lib.logger.logger import get_logger
from lib.settings.settings import Config, EnvConfig
from lib.utils.string_parser import insert_data

_log = get_logger(__file__, 'AuthServerLogger', 'logs/auth.log')
_config = Config().get()
_env_config = EnvConfig()
_api = API()
_auth = DiscordOAuth()
_pdb = PlayersDB()
_ds_api = DiscordApi()

def init_app(app: FastAPI) -> None:
    @app.get('/bot/auth/game', include_in_schema=False)
    async def game(
        region: Optional[str] = None,
        status: Optional[str] = None, 
        account_id: Optional[str] = None, 
        nickname: Optional[str] = None
        ):
        if region is not None and status is None:
            region = _api._reg_normalizer(region)
            response = RedirectResponse(
                insert_data(
                    _config.auth.wg_uri,
                    {
                        'region' : region,
                        'app_id' : next(_env_config.LT_APP_IDS) if region == 'ru' else next(_env_config.WG_APP_IDS),
                        'redirect_uri' : insert_data(
                            _config.auth.wg_redirect_uri,
                            {
                                'region' : region,
                            }
                        )
                    }    
                )
            )
            response.set_cookie(
                key='region',
                value=region
            )
            return response
        else:
            print(region, status, account_id, nickname)
            if status == 'ok':
                response = RedirectResponse(
                    insert_data(
                        _config.auth.ds_auth_primary_uri,
                        {
                            'client_id' : _env_config.CLIENT_ID,
                            'redirect_uri' : 
                                insert_data(
                                    _config.auth.ds_auth_redirect_url,
                                    {
                                        'region' : region
                                    }
                                )
                        }
                    )
                )
                response.set_cookie(
                    key = 'account_id',
                    value = account_id,
                )
                response.set_cookie(
                    key = 'nickname',
                    value = nickname,
                )
                return response
    
    @app.get('/bot/auth/discord', include_in_schema=False)
    async def discord(
        code: str = None, 
        nickname: Optional[str] = Cookie(None), 
        account_id: Optional[int] = Cookie(None),
        region: Optional[str] = Cookie(None),
        ):

        _log.debug(f'Region: {region}')
        if region not in _config.default.available_regions:
            return JSONResponse({'Error' : 'Unknown region in url'}, status_code=400)
        
        access_token = await _auth.exchange_code(code)
        user_data = await _ds_api.get_user_data(access_token)
        
        response = RedirectResponse(
            f'/bot/ui/register_success?user_name={user_data["username"]}&global_name={user_data["global_name"]}&nickname={nickname}'
        )
        
        player = DBPlayer(
            id=user_data['id'],
            game_id=account_id,
            nickname=nickname,
            region=region,
        )
        _pdb.set_member(player, override=True)
        _pdb.set_member_verified(user_data['id'])
        
        return response
    
    text_classes = 'rounded-xl flex bg-teal-400 w-full p-10 text-4xl'
    @ui.page('/register_success', title='Register Success', favicon='✅', dark=True)
    async def register_success(client: Client, user_name: str, global_name: str, nickname: str):
        await client.connected()
        ui.label('Registration complete').classes(text_classes)
        ui.label(f'Discord account: {user_name} | {global_name}').classes(text_classes)
        ui.label(f'Game account: {nickname}').classes(text_classes)
        await sleep(3)
        ui.notify('Registration complete! Check data and close this page.')
        return

    ui.run_with(app, mount_path='/bot/ui', storage_secret='kFJofle04kkKc9f9d90-elk4kFKl4kFJofle04kkKc9f9d90')