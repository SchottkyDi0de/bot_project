from typing import TYPE_CHECKING

from aiogram import Router

from lib.api import API
from lib.database.players import PlayersDB

from .set import SetHandlers
from .hook import HookHandlers
from .stats import StatsHandlers
from .session import SessionHandlers
from .profile import ProfileResponces
from .sv_settings import SVSettingsHandlers
from .parse_replay import ParseReplayHandlers
from .session_widget import SessionWidgetHandlers
from .image_settings import ImageSettingsHandlers

if TYPE_CHECKING:
    from aiogram import Bot, Dispatcher
    from aiogram.types import CallbackQuery


class ButtonsResponces(SetHandlers, 
                       HookHandlers,
                       StatsHandlers, 
                       SessionHandlers,
                       ProfileResponces,
                       SVSettingsHandlers,
                       ParseReplayHandlers,
                       SessionWidgetHandlers, 
                       ImageSettingsHandlers,):
    def __init__(self, bot: 'Bot', dp: 'Dispatcher') -> None:
        self.bot = bot
        self.api = API()
        self.pdb = PlayersDB()
        self.router = Router()
        
        self.router.callback_query.register(self.callback_handler)
        
        dp.include_router(self.router)

    async def callback_handler(self, data: 'CallbackQuery', **kwargs):
        await getattr(self, f"{data.data.split(':')[0]}_handle")(data, **kwargs)
