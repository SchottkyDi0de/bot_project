import asyncio
from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardButton

from lib.settings.settings import Config

from .base import ButtonList

from lib.database.players import PlayersDB
from lib.data_classes.db_player import ImageSettings
from lib.data_classes.state_data import ImageSettingsStateData
from lib.locale.locale import Text
from lib.utils import split_list2chunks

_config = Config().get()


class ImageSettingsButtons:
    @staticmethod
    def image_settings_buttons(state_data: ImageSettingsStateData, include_sv_settings: bool = False) -> ButtonList[InlineKeyboardButton]:
        buttons = []
        
        for name in ["bg", "theme", "colors", "other"]:
            buttons.append(InlineKeyboardButton(text=getattr(Text().get().cmds.image_settings.items.main_buttons, name), 
                           callback_data=f"image_settings_{name}"))
        
        if include_sv_settings:
            buttons.append(InlineKeyboardButton(text=Text().get().cmds.stats_view_settings.sub_descr.main_button,
                                                callback_data="sv_settings"))
        
        if state_data.base_image_settings != ImageSettings.model_validate({}) and \
            not state_data.resetted:
            buttons.append(InlineKeyboardButton(text=Text().get().cmds.image_settings.items.main_buttons.reset,
                                               callback_data="image_settings_reset"))

        if state_data.is_changed:
            buttons.append(InlineKeyboardButton(text=Text().get().cmds.image_settings.items.main_buttons.save,
                                               callback_data="image_settings_save"))
        return ButtonList(buttons)

    @staticmethod
    def image_settings_back_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text=Text().get().cmds.image_settings.items.main_buttons.back,
                                                callback_data="image_settings_back")])
    
    @staticmethod
    def image_settings_theme_buttons() -> ButtonList[list[InlineKeyboardButton]]:
        buttons = []
        for theme_name in _config.themes.available:
            buttons.append(InlineKeyboardButton(text=theme_name, 
                                                callback_data=f"image_settings_theme_set:{theme_name}"))
        return ButtonList(split_list2chunks(buttons, 2) + [ImageSettingsButtons.image_settings_back_buttons()])
    
    @staticmethod
    def image_settings_bg_buttons(from_user_id: int) -> ButtonList[list[InlineKeyboardButton]]:
        buttons = ImageSettingsButtons.image_settings_back_buttons()
        if asyncio.run(PlayersDB().get_member_image(from_user_id)) is not None:
            buttons.append(InlineKeyboardButton(text=Text().get().cmds.image_settings.sub_descr.reset_bg,
                                                callback_data="image_settings_reset_bg"))
        return ButtonList(buttons[::-1])

    @staticmethod
    def image_settings_colors_buttons() -> ButtonList[list[InlineKeyboardButton]]:
        buttons = []
        locale = Text().get().cmds.image_settings.items.colors_buttons

        for color in ["nickname_color", "clan_tag_color", "stats_color", "main_text_color", "stats_text_color",
                      "negative_stats_color", 'positive_stats_color']:
            buttons.append(InlineKeyboardButton(text=getattr(locale, color), 
                                                 callback_data=f"image_settings_color:{color}"))
        
        return ButtonList(split_list2chunks(buttons, 2) + [ImageSettingsButtons.image_settings_back_buttons()])

    @staticmethod
    def image_settings_colors_back_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text=Text().get().cmds.image_settings.items.main_buttons.back,
                                                callback_data="image_settings_colors_back")])

    @staticmethod
    def image_settings_other_buttons() -> ButtonList[list[InlineKeyboardButton]]:
        buttons = []
        tlist = []
        for name in ["use_custom_bg", "colorize_stats", "disable_flag", "hide_nickname", "hide_clan_tag",
                  "disable_stats_blocks", "disable_rating_stats", "disable_cache_label"]:
            tlist.append(InlineKeyboardButton(text=getattr(Text().get().cmds.image_settings.items.others_buttons, 
                                                           name), 
                                              callback_data=f"image_settings_other_param:{name}"))
        buttons += split_list2chunks(tlist, 2)
        tlist = []
        for name in ["glass_effect", "blocks_bg_brightness"]:
            tlist.append(InlineKeyboardButton(text=getattr(Text().get().cmds.image_settings.items.others_buttons, 
                                                           name), 
                                              callback_data=f"image_settings_other_{name}"))
        buttons += split_list2chunks(tlist, 2)
        return ButtonList(buttons + [ImageSettingsButtons.image_settings_back_buttons()])
    
    @staticmethod
    def image_settings_other_back_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text=Text().get().cmds.image_settings.items.main_buttons.back,
                                                callback_data="image_settings_other_back")])

    @staticmethod
    def image_settings_other_onoff_buttons() -> ButtonList[InlineKeyboardButton]:
        buttons = ButtonList([])
        for name, data in zip(("on_", "off_"), (1, 0)):
            buttons.append(
                InlineKeyboardButton(
                    text=getattr(Text().get().cmds.image_settings.items.others_buttons, name),
                    callback_data=f"image_settings_other_on_off:{data}"
                    )
                )
        buttons += ImageSettingsButtons.image_settings_other_back_buttons()
        return buttons
