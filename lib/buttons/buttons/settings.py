from aiogram.types import InlineKeyboardButton

from lib.locale.locale import Text

from .base import ButtonList


class SettingsButtongs:
    @staticmethod
    def settings_buttons() -> ButtonList:
        data = []
        locale = Text().get().cmds.settings.sub_descr.buttons
        for text, callback in ((locale.profile, "profile_settings"), (locale.image, "image_settings"),
                               (locale.session_widget, "session_widget")):
            data.append(InlineKeyboardButton(text=text, callback_data=callback))
        return ButtonList(data)
    
    @staticmethod
    def profile_reg_buttons() -> ButtonList:
        return ButtonList([InlineKeyboardButton(text=Text().get().cmds.settings.sub_descr.buttons.profile_reg, 
                                                callback_data="profile_reg")])
