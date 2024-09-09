from aiogram.types import InlineKeyboardButton

from lib.settings.settings import Config

from lib.data_classes.state_data import SVSettingsStateData
from lib.locale.locale import Text

from .base import ButtonList

_config = Config().get()


class SVSettingsButtons:
    @staticmethod
    def sv_settings_buttons(state_data: SVSettingsStateData) -> ButtonList:
        buttons = ButtonList([
            InlineKeyboardButton(text=f"slot {i}", callback_data=f"sv_settings_slot:{i}") for i in range(1, 5)
        ])
        if not state_data.is_changed:
            buttons.append(InlineKeyboardButton(text="Rating" + (" ✅" * state_data.rating), 
                                                callback_data="sv_settings_rating"))
        if state_data.is_changed:
            buttons.append(InlineKeyboardButton(text=Text().get().cmds.stats_view_settings.sub_descr.save, 
                                                callback_data="sv_settings_save"))
        return buttons

    @staticmethod
    def sv_settings_slot_buttons(rating: bool) -> ButtonList:
        stats = _config.image.available_stats if not rating else _config.image.available_rating_stats
        return ButtonList([
            InlineKeyboardButton(text=i, callback_data=f"sv_settings_slot_set:{i}") for i in stats
        ])
    