from __future__ import annotations
from typing import TYPE_CHECKING

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, Message

from lib.utils import split_list2chunks

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery


class ButtonList(list):
    def __init__(self, buttons: list | list[list] | None = None, formmated: bool=False):
        self.formmated = formmated
        super().__init__(buttons if buttons else [])
    
    def __add__(self, other) -> ButtonList:
        if isinstance(other, ButtonList):
            self.formmated = self.formmated or other.formmated

        return ButtonList(super().__add__(other), formmated=self.formmated)
    
    @staticmethod
    def _get_keyboard(buttons: list, 
                      button_in_row: int | None, 
                      formatted: bool=False) -> ReplyKeyboardMarkup | InlineKeyboardMarkup:
        if not formatted and button_in_row:
            buttons = split_list2chunks(buttons, button_in_row)

        if not buttons[0:]:
            return InlineKeyboardMarkup(inline_keyboard=[])

        if isinstance(buttons[0][0], KeyboardButton):
            return ReplyKeyboardMarkup(keyboard=buttons)
        else:
            return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @classmethod
    def load_from_data(cls, data: 'Message | CallbackQuery') -> ButtonList:
        msg = data if isinstance(data, Message) else data.message
        return cls(msg.reply_markup.inline_keyboard, formmated=True)

    @property
    def is_empty(self) -> bool:
        return len(self) == 0
    
    def format_data(self, button_in_row: int) -> ButtonList:
        if self.formmated:
            return self
        self.formmated = True
        self[:] = split_list2chunks(self, button_in_row)
        return self
    
    def get_keyboard(self, button_in_row: int | None=3) -> ReplyKeyboardMarkup | InlineKeyboardMarkup:
        return self._get_keyboard(self, button_in_row, self.formmated)
