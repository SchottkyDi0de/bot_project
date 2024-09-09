from aiogram.types import InlineKeyboardButton, KeyboardButton

from .base import ButtonList


class SessionButtons:
    @staticmethod
    def get_session_buttons(author_id: int) -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text="🔄", callback_data=f"get_session:{author_id}")])

    @staticmethod
    def start_autossession_timezone_buttons() -> ButtonList[KeyboardButton]:
        return ButtonList([KeyboardButton(text="0")])

    @staticmethod
    def start_autossesion_restart_buttons() -> ButtonList[KeyboardButton]:
        return ButtonList([KeyboardButton(text="00:00")])