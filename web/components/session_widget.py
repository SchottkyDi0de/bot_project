from typing import Optional, Tuple
from time import sleep

from fastapi import FastAPI
from nicegui import ui, Client, run

from lib.database.players import PlayersDB
from lib.exceptions.database import *
from lib.api.async_wotb_api import API, _log as _api_log
from lib.data_classes.api.api_data import PlayerGlobalData
from lib.image.session import ImageGenSession, ImageGenReturnTypes, _log as _image_log
from lib.data_parser.parse_data import get_session_stats, _log as _parser_log
from lib.settings.settings import Config
from lib.data_classes.db_player import AccountSlotsEnum
from lib.utils.standard_account_validate import standard_account_validate

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
            p_id: int, 
            slot_n: int,
            lang: Optional[str] = None,
            bg_color: Optional[str] = None,
        ) -> None:
        body_css = f'body {{background-color: rgba{"(100,100,100,1)" if bg_color is None else bg_color}}}'
        ui.add_css(
            body_css
        )
        
        try:
            game_account, member, slot = await standard_account_validate(account_id=p_id, slot=AccountSlotsEnum(slot_n))
        except MemberNotFound:
            ui.label('Player not found')
            return
        except SlotIsEmpty:
            ui.label('No data in specified slot')
            return
        except PremiumSlotAccessAttempt:
            ui.label('Premium not found for access to specified slot')
            return
        
        try:
            await _pdb.check_member_last_stats(slot=slot, member=member)
        except LastStatsNotFound:
            ui.label('Session not found')
            return
        
        await client.connected()

        stats = await _api.get_stats(game_account.region, game_account.game_id, ignore_lock=True)
        last_stats = PlayerGlobalData.model_validate(game_account.last_stats)
        
        diff_battles = (
            stats.data.statistics.all.battles - last_stats.data.statistics.all.battles,
            stats.data.statistics.rating.battles - last_stats.data.statistics.rating.battles
        )
        
        last_diff_battles = diff_battles
        session_data = await get_session_stats(last_stats, stats, zero_bypass=True)

        session_image = _img.generate(
            data=stats,
            diff_data=session_data,
            player=member,
            slot=slot,
            force_locale=lang,
            widget_mode=True,
            server=None,
            output_type=ImageGenReturnTypes.PIL_IMAGE
        )
            
        ui.image(session_image)\
            .classes('w-full')\
        
        async def check_user_stats():
            last_stats = PlayerGlobalData.model_validate(game_account.last_stats)
            if last_stats is None:
                return ui.label('Session not found')

            stats = await _api.get_stats(game_account.region, game_account.game_id, ignore_lock=True)
            diff_battles = (
                stats.data.statistics.all.battles - last_stats.data.statistics.all.battles,
                stats.data.statistics.rating.battles - last_stats.data.statistics.rating.battles
            )
            if diff_battles != last_diff_battles:
                ui.run_javascript('window.location.reload()')
                
        ui.timer(float(game_account.widget_settings.update_time), check_user_stats)
        
    ui.run_with(app, mount_path='/bot/ui', storage_secret='kFJofle04kkKc9f9d90-elk4kFKl4kdJofle04kkKc9f9d90')

