import traceback
from asyncio import sleep
from typing import Annotated, Optional
from urllib import parse

from fastapi import Cookie, FastAPI, Header, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from pywebio.output import *
from pywebio.platform.fastapi import asgi_app
from pywebio.session import eval_js, run_asyncio_coroutine, run_js
from pywebio import config
import uvicorn

from lib.data_classes.db_player import DBPlayer, ImageSettings
from lib.data_classes.internal_api.err_response import ErrorResponse
from lib.data_classes.internal_api.inf_response import InfoResponse
from lib.database.players import PlayersDB
from lib.data_classes.internal_api.restart_session import SessionState
from lib.exceptions.data_parser import NoDiffData
from lib.internal_api.responses import ErrorResponses, InfoResponses
from lib.logger.logger import get_logger
from lib.settings.settings import Config, EnvConfig
from lib.api.async_discord_api import DiscordApi
from lib.auth.discord import DiscordOAuth
from lib.api.async_wotb_api import API
from lib.image.session import ImageGen, ImageOutputType
from lib.data_parser.parse_data import get_normalized_data, get_session_stats
from lib.data_classes.image import ImageGenExtraSettings
from lib.exceptions.api import APIError
from lib.utils.string_parser import insert_data

_pdb = PlayersDB()
_env_config = EnvConfig()
_config = Config().get()
_log = get_logger(__file__, 'ServerLogger', 'logs/server.log')
_auth = DiscordOAuth()
_ds_api = DiscordApi()
_api = API()
_image = ImageGen()

app = FastAPI(docs_url='/bot/api/docs')

class AllUsers(BaseModel):
    count: int


class AllSessions(BaseModel):
    count: int


def _get_query_params(request: str) -> dict:
    return dict(parse.parse_qsl(request.lstrip('?')))

def _get_spec_param(query_params: dict, param_name: str) -> str | None:
    return query_params.get(param_name, None)

@config(title='Auth Complete', theme='dark')
def auth_complete():
    query_params = _get_query_params(eval_js('window.location.search'))
    
    user_name = _get_spec_param(query_params, 'user_name')
    global_name = _get_spec_param(query_params, 'global_name')
    game_nickname = _get_spec_param(query_params, 'nickname')
    if user_name is None or global_name is None or game_nickname is None:
        put_error('# ❌ Registration failed, please try again ❌')
        return
    
    put_markdown('# 🎉 Registration is complete, you can close the page 🎉')
    put_info(f'Authorized as: {user_name} | {global_name}')
    put_info(f'Game account: {game_nickname}')
    
    
@config(title='Blitz Statistics Widget')
async def session_widget_app():
    with use_scope('root', clear=True):
        raw_query = await eval_js('window.location.search')
        query_params = _get_query_params(raw_query)
        
        player_id = _get_spec_param(query_params, 'player_id')
        
        if player_id is None:
            put_info('No player ID specified!', closable=True)
            return
        
        player_id = int(player_id)
        
        
        if not _pdb.check_member(player_id):
            put_info('Member not found!', closable=True)
            return
        
        member = _pdb.get_member(player_id)
        
        if not _pdb.check_member_last_stats(player_id):
            put_info('Active session not found!', closable=True)
            return
        
        
        last_stats = _pdb.get_member_last_stats(player_id)
        new_stats = await run_asyncio_coroutine(
            _api.get_stats(
                game_id=member.game_id, 
                region=member.region,
                ignore_lock=True
                )
        )
        new_stats_normalized = get_normalized_data(new_stats)

        session_stats = get_session_stats(last_stats, new_stats, zero_bypass=True)
            
        extra = ImageGenExtraSettings()
        # extra.disable_bg = True
        # extra.stats_blocks_color = (0, 0, 0, 245)
        
        while True:
            try:
                new_stats = await run_asyncio_coroutine(
                    _api.get_stats(
                        game_id=member.game_id, 
                        region=member.region,
                        ignore_lock=True
                    )
                )
            except APIError:
                _log.debug('API error')
                continue
            
            new_stats_normalized = get_normalized_data(new_stats)
            
            if session_stats is not None:
                image = _image.generate(
                    data=new_stats_normalized, 
                    diff_data=session_stats,
                    ctx=None,
                    player=member,
                    server_settings=None,
                    extra=extra,
                    output_type=ImageOutputType.pil_image,
                    widget_mode=True
                )
                put_image(image, format='png').style('background: rgba(0, 0, 0, 0);')
            else:
                put_info('No session data, play some battles.', closable=True)

            await run_asyncio_coroutine(sleep(60))
            run_js('window.location.reload()')

class Server:
    def __init__(self):
        self.app = app
        self.app.mount('/bot/register_success', asgi_app(auth_complete))
        self.app.mount('/bot/session_widget_app', asgi_app(session_widget_app))
    
    @app.get('/', include_in_schema=False)
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
    
    @app.get('/bot/auth/discord', include_in_schema=False)
    async def auth(
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
            f'/bot/register_success?user_name={user_data["username"]}&global_name={user_data["global_name"]}&nickname={nickname}'
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
        
    @app.get('/bot/auth/game', include_in_schema=False)
    async def game_auth(
        region: Optional[str] = None,
        status: Optional[str] = None, 
        account_id: Optional[str] = None, 
        nickname: Optional[str] = None
        ):
        if region is not None and status is None:
            response = RedirectResponse(
                insert_data(
                    _config.auth.wg_uri,
                    {
                        'region' : _api._reg_normalizer(region),
                        'app_id' : next(_env_config.LT_APP_IDS) if region == 'ru' else next(_env_config.WG_APP_IDS),
                        'redirect_uri' : insert_data(
                            _config.auth.wg_redirect_uri,
                            {
                                'host' : _config.server.host,
                                'port' : _config.server.port
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
                                        'host' : _config.server.host,
                                        'port' : _config.server.port
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
    def get_image_settings(api_key: Annotated[str, Header()], discord_id: str | int) -> ImageSettings | ErrorResponse:
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
    def set_image_settings(api_key: Annotated[str, Header()], discord_id: str | int, image_settings: ImageSettings) -> InfoResponse | ErrorResponse:
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
    def get_all_users(api_key: Annotated[str, Header()]) -> AllUsers | ErrorResponse:
        if api_key != _env_config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
        
        users = _pdb.count_members()
        return JSONResponse({'count' : users}, status_code=200)

    @app.get('/bot/api/get_all_sessions', responses={
        418: {'model' : ErrorResponse, 'description' : 'Access denied'},
        200: {'model' : AllSessions, 'description' : 'All sessions'}
        }
    )
    def get_all_sessions(api_key: Annotated[str, Header()]) -> AllSessions | ErrorResponse:
        if api_key != _env_config.INTERNAL_API_KEY:
            return JSONResponse(ErrorResponses.access_denied.model_dump(), status_code=ErrorResponses.access_denied.code)
        
        sessions = _pdb.count_sessions()
        return JSONResponse({'count' : sessions}, status_code=200)
    
def run():
    server = Server()
    return server.app
    

if __name__ == '__main__':
    uvicorn.run(Server().app, host=_config.server.host, port=_config.server.port)