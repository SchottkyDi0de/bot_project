from typing import Optional
from asyncio import sleep

from fastapi import Cookie, FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from nicegui import ui, Client

from lib.api.async_discord_api import DiscordApi
from lib.api.async_wotb_api import API
from lib.auth.discord import DiscordOAuth
from lib.data_classes.db_player import AccountSlotsEnum, DBPlayer
from lib.database.players import PlayersDB
from lib.logger.logger import get_logger
from lib.settings.settings import Config, EnvConfig
from lib.utils.string_parser import insert_data
from lib.utils.standard_account_validate import standard_account_validate

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
        account_id: Optional[int] = None,
        requested_by: Optional[int] = None,
        nickname: Optional[str] = None,
        slot_n: Optional[int] = None
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
                                'requested_by': requested_by,
                                'slot' : slot_n
                            }
                        )
                    }    
                )
            )
            response.set_cookie(
                key='region',
                value=region
            )
            response.set_cookie(
                key='requested_by',
                value=requested_by
            )
            response.set_cookie(
                key='slot_n',
                value=str(slot_n)
            )
            return response
        else:
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
            else:
                return JSONResponse({'Error' : 'Unknown status in url'}, status_code=400)
    
    @app.get('/bot/auth/discord', include_in_schema=False)
    async def discord(
        code: str = None, 
        nickname: Optional[str] = Cookie(None), 
        account_id: Optional[int] = Cookie(None),
        requested_by: Optional[int] = Cookie(None),
        slot_n: Optional[int] = Cookie(None),
        region: Optional[str] = Cookie(None),
        ):

        _log.info(f'Requested by {requested_by}, account_id: {account_id}, nickname: {nickname}, slot_n: {slot_n}, region: {region}')
        if region not in _config.default.available_regions:
            return JSONResponse({'Error' : 'Unknown region in url'}, status_code=400)
        
        try:
            game_account, member, slot = await standard_account_validate(
                account_id=requested_by,
                slot=AccountSlotsEnum(slot_n),
            )
        except Exception:
            return JSONResponse({'Error' : 'Account validation failed'}, status_code=400)
        
        access_token = await _auth.exchange_code(code)
        user_data = await _ds_api.get_user_data(access_token)
        
        if int(user_data['id']) != requested_by:
            return JSONResponse({'Error' : 'Access denied, account id mismatch'}, status_code=400)
        
        if game_account.game_id != account_id:
            return JSONResponse({'Error' : 'Access denied, game id mismatch'}, status_code=400)
        
        await _pdb.set_verification(member_id=member.id, slot=slot, verified=True)
        
        response = RedirectResponse(
            f'/bot/ui/register_success?user_name={user_data["username"]}&global_name={user_data["global_name"]}&nickname={nickname}'
        )
        
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