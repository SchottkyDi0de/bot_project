from aiogram.types import InlineKeyboardButton

from lib.settings.settings import Config

from lib.data_classes.db_player import HookStatsTriggers
from lib.locale.locale import Text

from .base import ButtonList

_config = Config().get()


class HookButtons:
    @staticmethod
    def hook_buttons() -> ButtonList[InlineKeyboardButton]:
        buttons = ButtonList()
        for button in [
                            InlineKeyboardButton(text=Text().get().cmds.hook.buttons.new_hook, 
                                                 callback_data="new_hook"),
                            InlineKeyboardButton(text=Text().get().cmds.hook.buttons.hook_state, 
                                                 callback_data="hook_state"),
                            InlineKeyboardButton(text=Text().get().cmds.hook.buttons.disable_hook,
                                                 callback_data="disable_hook")
                       ]:
            buttons.append(button)
        return buttons
    
    @staticmethod
    def hook_region_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([
            InlineKeyboardButton(text=f"{region.capitalize()}", callback_data=f"hook_region:{region}")
            for region in _config.default.available_regions
        ])
    
    @staticmethod
    def hook_target_stats_buttons() -> ButtonList[InlineKeyboardButton]:
        available_stats = [
            "winrate",
            "avg_damage",
            "battles",
            "hits",
            "losses",
            "wins"
        ]
        return ButtonList([
            InlineKeyboardButton(text=stats_name.replace("_", " ").capitalize(), 
                                 callback_data=f"hook_target_stats:{stats_name}")
            for stats_name in available_stats
        ])

    @staticmethod
    def hook_rating_buttons() -> ButtonList[InlineKeyboardButton]:
        available_stats = [
            "winrate",
            "avg_damage",
            "battles",
            "hits",
            "losses",
            "wins",
            "rating",
            "leaderboard_position"
        ]
        return ButtonList([
            InlineKeyboardButton(text=stats_name.replace("_", " ").capitalize(),
                                 callback_data=f"hook_target_stats:{stats_name}")
            for stats_name in available_stats
        ])

    @staticmethod
    def hook_rating_onoff_buttons(set_on: bool) -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text="Rating" + (" ✅" * set_on), 
                                                callback_data=f"hook_rating_param:{int(not set_on)}")])

    @staticmethod
    def hook_target_trigger_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([
            InlineKeyboardButton(text=x.name.replace("_", " ").capitalize(), 
                                 callback_data=f"hook_target_trigger:{x.name}")
            for x in HookStatsTriggers
        ])
    
    @staticmethod
    def hook_watch_for_buttons() -> ButtonList[InlineKeyboardButton]:
        buttons = ButtonList()
        for name in ["main", "session", "diff"]:
            buttons.append(InlineKeyboardButton(text=getattr(Text().get().cmds.hook.buttons, name), 
                                                callback_data=f"hook_watch_for:{name}"))
        return buttons
