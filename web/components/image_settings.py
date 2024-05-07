from typing import Optional
from time import sleep

from fastapi import FastAPI
from nicegui import ui, Client, run

from lib.database.players import PlayersDB
from lib.exceptions.database import LastStatsNotFound
from lib.api.async_wotb_api import API, _log as _api_log
from lib.data_classes.api.api_data import PlayerGlobalData
from lib.image.session import ImageGen, ImageOutputType, _log as _image_log
from lib.data_parser.parse_data import get_session_stats, _log as _parser_log
from lib.settings.settings import Config

_api = API()
_config = Config().get()
_pdb = PlayersDB()
_img = ImageGen()

_api_log.setLevel(40)
_image_log.setLevel(40)
_parser_log.setLevel(40)

async def init_app(app: FastAPI) -> None:
    @ui.page('/image_settings', favicon='⚙️', title='Image Settings')
    async def d() -> str:
        return 'work in progress'