from typing import Optional, Tuple
from time import sleep

from fastapi import FastAPI
from nicegui import ui, Client, run

from lib.database.players import PlayersDB
from lib.exceptions.database import LastStatsNotFound
from lib.api.async_wotb_api import API, _log as _api_log
from lib.data_classes.api.api_data import PlayerGlobalData
from lib.image.session import ImageGenSession, ImageOutputType, _log as _image_log
from lib.data_parser.parse_data import get_session_stats, _log as _parser_log
from lib.settings.settings import Config

_api = API()
_pdb = PlayersDB()
_img = ImageGenSession()

_api_log.setLevel(40)
_image_log.setLevel(40)
_parser_log.setLevel(40)

def init_app(app: FastAPI) -> None:

    @ui.page(
        '/session_widget_app', 
        favicon='🎲', 
        title='Session Widget',
        response_timeout=6.0,
    )
    async def session_widget_app(
            client: Client,
            p_id: Optional[int] = None, 
            lang: Optional[str] = None,
            bg_color: Optional[str] = None
        ) -> None:
        print(f'bg_color: {bg_color}')
        ui.add_css(
            f'body {{background-color: rgba{"(0,0,0,0)" if bg_color is None else bg_color};}}',
        )
        
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
        
        await client.connected()
        
        user = _pdb.get_member(p_id)
        stats = await _api.get_stats(user.region, user.game_id, ignore_lock=True)
        last_stats = PlayerGlobalData.model_validate(user.last_stats)
        
        diff_battles = (
            stats.data.statistics.all.battles - last_stats.data.statistics.all.battles,
            stats.data.statistics.rating.battles - last_stats.data.statistics.rating.battles
        )
        
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
            force_locale=lang,
            debug_label=False
        )
        
        ui.image(session_image)\
            .classes('w-full')\
        
        async def check_user_stats():
            user = _pdb.get_member(p_id)
            last_stats = PlayerGlobalData.model_validate(user.last_stats)
            if last_stats is None:
                return ui.label('Session not found')

            stats = await _api.get_stats(user.region, user.game_id, ignore_lock=True)
            diff_battles = (
                stats.data.statistics.all.battles - last_stats.data.statistics.all.battles,
                stats.data.statistics.rating.battles - last_stats.data.statistics.rating.battles
            )
            if diff_battles != last_diff_battles:
                ui.run_javascript('window.location.reload()')
                
        ui.timer(float(user.widget_settings.update_time), check_user_stats)
        
    ui.run_with(app, mount_path='/bot/ui', storage_secret='kFJofle04kkKc9f9d90-elk4kFKl4kdJofle04kkKc9f9d90')