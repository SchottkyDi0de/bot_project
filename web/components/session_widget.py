from typing import Optional
from asyncio import sleep

from fastapi import FastAPI
from nicegui import ui, Client
from nicegui import app as _app

from lib.database.players import PlayersDB
from lib.exceptions.database import LastStatsNotFound
from lib.api.async_wotb_api import API
from lib.data_classes.api.api_data import PlayerGlobalData
from lib.image.session import ImageGen, ImageOutputType
from lib.data_parser.parse_data import get_session_stats
from lib.settings.settings import Config

_api = API()
_config = Config().get()
_pdb = PlayersDB()
_img = ImageGen()


def init_app(app: FastAPI) -> None:
    @ui.page(
        '/session_widget_app', 
        favicon='🎲', 
        title='Session Widget',
        response_timeout=6.0,
        dark=True
    )
    async def session_widget_app(
            client: Client,
            p_id: Optional[int] = None, 
            lang: Optional[str] = None, 
        ) -> None:
        
        if p_id is None:
            ui.label('Player id not specified')
            return
        
        if not _pdb.check_member(p_id):
            ui.label('Player not found')
            return
        
        try:
            _pdb.check_member_last_stats(p_id)
        except LastStatsNotFound:
            ui.label('Session not found')
            return
        _app.storage.browser[client.id] = 'Active session'
        
        await client.connected()
        user = _pdb.get_member(p_id)
        stats = await _api.get_stats(user.region, user.game_id, ignore_lock=True)
        last_stats = PlayerGlobalData.model_validate(user.last_stats)
        
        diff_battles = (
            stats.data.statistics.all.battles - last_stats.data.statistics.all.battles,
            stats.data.statistics.rating.battles - last_stats.data.statistics.rating.battles
        )
        print(diff_battles)
        
        last_diff_battles = diff_battles
        session_data = get_session_stats(last_stats, stats, zero_bypass=True)

        session_image = _img.generate(
            stats, 
            session_data, 
            ctx=None, 
            server_settings=None, 
            player=user, 
            widget_mode=True,
            output_type=ImageOutputType.pil_image,
            force_locale=lang
        )
        
        ui.image(session_image)\
            .classes('w-2/3')\
            .classes('mx-auto')
            
        for _ in range(10000):
            stats = await _api.get_stats(user.region, user.game_id, ignore_lock=True)
            diff_battles = (
                stats.data.statistics.all.battles - last_stats.data.statistics.all.battles,
                stats.data.statistics.rating.battles - last_stats.data.statistics.rating.battles
            )
            if diff_battles != last_diff_battles:
                ui.run_javascript('window.location.reload()')
                
            await sleep(user.widget_settings.update_per_seconds // 4)
        
    ui.run_with(app, mount_path='/bot', storage_secret='kFJofle04kkKc9f9d90-elk4kFKl4kFJofle04kkKc9f9d90')