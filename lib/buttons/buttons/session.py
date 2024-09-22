from aiogram.types import InlineKeyboardButton, KeyboardButton

from lib.locale.locale import Text

from .base import ButtonList


class SessionButtons:
    @staticmethod
    def session_main_buttons(member_has_last_stats: bool) -> ButtonList[InlineKeyboardButton]:
        buttons = ButtonList()
        buttons.append(InlineKeyboardButton(text=Text().get().cmds.session.sub_descr.buttons.start_session, 
                                            callback_data="session_start_session"))
        if member_has_last_stats:
            buttons.append(InlineKeyboardButton(text=Text().get().cmds.session.sub_descr.buttons.stop_session,
                                                callback_data="session_stop_session"))
            buttons.append(InlineKeyboardButton(text=Text().get().cmds.session.sub_descr.buttons.get_session,
                                                callback_data="session_get_session"))
        return buttons
    
    @staticmethod
    def session_get_session_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text="🔄", callback_data="session_get_session")])
    
    @staticmethod
    def session_start_session_buttons(is_autosession: bool) -> ButtonList[InlineKeyboardButton]:
        buttons = ButtonList()
        buttons.append(InlineKeyboardButton(text=Text().get().cmds.session.sub_descr.buttons.autosession + \
                                            (" ✅" if is_autosession else " ❌"),
                                            callback_data="session_autosession"))
        if is_autosession:
            buttons.append(InlineKeyboardButton(text=Text().get().cmds.session.sub_descr.buttons.timezone,
                                                callback_data="session_timezone"))
            buttons.append(InlineKeyboardButton(text=Text().get().cmds.session.sub_descr.buttons.restart_time,
                                                callback_data="session_restart_time"))
        buttons.append(InlineKeyboardButton(text=Text().get().cmds.session.sub_descr.buttons.start_session,
                                            callback_data="session_fstart_session"))
        return buttons

    @staticmethod
    def session_timezone_buttons() -> ButtonList[InlineKeyboardButton]:
        buttons = ButtonList()
        for i in range(13):
            buttons.append(InlineKeyboardButton(text=str(i), callback_data=f"session_set_timezone:{i}"))
        return buttons.format_data(6) + SessionButtons.session_back_buttons()
    
    @staticmethod
    def session_restart_time_buttons() -> ButtonList[InlineKeyboardButton]:
        buttons = ButtonList()
        for i in range(23):
            buttons.append(InlineKeyboardButton(text=str(i), callback_data=f"session_set_restart_time:{i}"))
        return buttons.format_data(6) + SessionButtons.session_back_buttons()

    @staticmethod
    def session_back_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text=Text().get().cmds.session.sub_descr.buttons.back,
                                                callback_data="session_back")]).format_data(1)

    @staticmethod
    def get_session_buttons(author_id: int) -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text="🔄", callback_data=f"get_session:{author_id}")])

    @staticmethod
    def start_autossession_timezone_buttons() -> ButtonList[KeyboardButton]:
        return ButtonList([KeyboardButton(text="0")])

    @staticmethod
    def start_autossesion_restart_buttons() -> ButtonList[KeyboardButton]:
        return ButtonList([KeyboardButton(text="00:00")])