from typing import Literal

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove

from .set import SetButtons
from .hook import HookButtons
from .common import CommonButtons
from .session import SessionButtons
from .settings import SettingsButtongs
from .sv_settings import SVSettingsButtons
from .parse_replay import ParseReplayButtons
from .image_settings import ImageSettingsButtons
from .session_widget import SessionWidgetButtons


class Buttons(SetButtons, 
              HookButtons,
              CommonButtons,
              SessionButtons, 
              SettingsButtongs, 
              SVSettingsButtons, 
              ParseReplayButtons, 
              SessionWidgetButtons, 
              ImageSettingsButtons):
    @staticmethod
    def remove_buttons(markup_type: Literal["reply", "inline"]) -> InlineKeyboardMarkup | ReplyKeyboardRemove:
        return (ReplyKeyboardRemove() if markup_type == "reply" else InlineKeyboardMarkup(inline_keyboard=[]))
