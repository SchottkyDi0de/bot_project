from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardButton

from lib.settings.settings import Config

from .base import ButtonList

if TYPE_CHECKING:
    from lib.data_classes.db_player import GameAccount

_config = Config().get()


class SetButtons:
    @staticmethod
    def set_player_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text=i, 
                                                callback_data=f"set_player:{i}") 
                           for i in _config.default.available_regions])

    @staticmethod
    def set_lang_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text=i, callback_data=f"set_lang:{i}") for i in 
                           [i for i in _config.default.available_locales if i != "auto"]])
    
    @staticmethod
    def sp_choose_slot(game_accounts: dict[str, 'GameAccount | None'], has_premium: bool) -> ButtonList[InlineKeyboardButton]:
        buttons = []
        for slot, account in game_accounts.items():
           buttons.append(InlineKeyboardButton(text=account.nickname if account else slot.split("_")[1], 
                                               callback_data=f"sp_choose_slot:{slot}")) 
        if not has_premium:
            buttons = buttons[:2]
        return ButtonList(buttons)
