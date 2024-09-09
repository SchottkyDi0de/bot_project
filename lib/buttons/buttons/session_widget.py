from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardButton

from lib.locale.locale import Text
from lib.data_classes.db_player import WidgetSettings

from .base import ButtonList

if TYPE_CHECKING:
    from lib.data_classes.state_data import WidgetSettingsStateData


class SessionWidgetButtons:
    @staticmethod
    def session_widget_buttons(link: str) -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text="link", url=link)])
    
    @staticmethod
    def session_widget_settings_buttons(state_data: 'WidgetSettingsStateData') -> ButtonList[InlineKeyboardButton]:
        buttons = ButtonList([InlineKeyboardButton(text=Text().get().cmds.session_widget.settings.buttons.edit, 
                                                   callback_data="session_widget_settings_edit")])
        if not state_data.resetted and state_data.current_widget_settings != WidgetSettings():
            buttons.append(InlineKeyboardButton(text=Text().get().cmds.session_widget.settings.buttons.reset, 
                                                callback_data="session_widget_settings_reset"))
        
        if state_data.current_widget_settings != state_data.base_widget_settings:
            buttons.append(InlineKeyboardButton(text=Text().get().cmds.session_widget.settings.buttons.save, 
                                                callback_data="session_widget_settings_save"))
        return buttons
    
    @staticmethod
    def session_widget_settings_edit_buttons(state_data: 'WidgetSettingsStateData') -> ButtonList[InlineKeyboardButton]:
        buttons = ButtonList()
        for name in [
                         "max_stats_blocks", 
                         "max_stats_small_blocks",
                         "background_transparency",
                         "stats_block_color",
                         "update_time"
                    ]:
            buttons.append(InlineKeyboardButton(
                text=getattr(Text().get().cmds.session_widget.settings.buttons.edit_buttons, name),
                callback_data=f"session_widget_settings_edit_io:{name}"
            ))
        
        for name in [
            "disable_bg",
            "disable_nickname",
            "disable_main_stats_block",
            "use_bg_for_stats_blocks",
            "adaptive_width",
        ]:
            buttons.append(InlineKeyboardButton(
                text=getattr(Text().get().cmds.session_widget.settings.buttons.edit_buttons, name),
                callback_data=f"session_widget_settings_edit_bool:{name}"
            ))

        if not (state_data.base_widget_settings.is_default and not state_data.is_settings_changed):
            buttons.extend(SessionWidgetButtons.session_widget_settings_back_buttons())

        return buttons
    
    @staticmethod
    def session_widget_settings_edit_onoff_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text=getattr(Text().get().cmds.session_widget.settings.buttons, name),
                                                callback_data=f"session_widget_settings_edit_onoff:{num}")
                                                for num, name in [("1", "_on"), ("0", "_off")]])

    @staticmethod
    def session_widget_settings_back_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text=Text().get().cmds.session_widget.settings.buttons.back, 
                                                callback_data="session_widget_settings_back")])
    
    @staticmethod
    def session_widget_settings_edit_back_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text=Text().get().cmds.session_widget.settings.buttons.back, 
                                                callback_data="session_widget_settings_edit_back")])
