from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardButton

from lib.locale.locale import Text
from lib.settings import Config

from .base import ButtonList

if TYPE_CHECKING:
    from lib.data_classes.replay_data_parsed import ParsedReplayData, Player

_config = Config().get()


class ParseReplayButtons:
    @staticmethod
    def parse_replay_main_back_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text=Text().get().cmds.parse_replay.items.buttons.main_back,
                                                callback_data="parse_replay_main_back")])


    @staticmethod
    def pr_region_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text=i.upper(), callback_data=f"pr_region:{i}") 
                           for i in _config.default.available_regions])
    
    @staticmethod
    def pr_main_buttons(replay_data: 'ParsedReplayData') -> ButtonList[InlineKeyboardButton]:
        buttons = [
            InlineKeyboardButton(text=f"Team {i}", callback_data=f"pr_team:{i}") for i in range(1, 3)
        ]
        buttons[replay_data.author.team_number - 1].text += "👤"
        if replay_data.winner_team_number is not None:
            buttons[replay_data.winner_team_number - 1].text += "🏆"

        return ButtonList(buttons)

    @staticmethod
    def pr_back_buttons() -> ButtonList[InlineKeyboardButton]:
        return ButtonList([InlineKeyboardButton(text=Text().get().cmds.parse_replay.items.buttons.back,
                                                callback_data="pr_back")])

    @staticmethod
    def pr_team_buttons(team: 'list[Player]', team_number: int) -> ButtonList[InlineKeyboardButton]:
        buttons = [
            InlineKeyboardButton(text=player.info.nickname, callback_data=f"pr_player:{team_number}:{ind}")
            for ind, player in enumerate(team)
        ]
        return ButtonList(sorted(buttons, key=lambda x: x.text)) + ParseReplayButtons.pr_back_buttons()
