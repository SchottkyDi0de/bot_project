from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardButton

from .base import ButtonList

if TYPE_CHECKING:
    from aiogram.types import User


class CommonButtons:
    @staticmethod
    def help_buttons(bot: 'User') -> ButtonList[InlineKeyboardButton]:
        return ButtonList([
            InlineKeyboardButton(text='Inline', 
                                 switch_inline_query_current_chat=f"<nickname> <region>"),
        ])
