from typing import TYPE_CHECKING, Callable, Literal

from aiogram.types import InlineKeyboardButton

from lib.database.players import PlayersDB
from lib.data_classes.db_player import DBPlayer

from ..buttons.base import ButtonList

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message


def _handle_return_data(rdata: tuple[tuple, dict, ButtonList] 
                        | tuple[tuple, dict] 
                        | tuple[tuple] 
                        | None) -> tuple[tuple, dict, ButtonList]:
    if rdata is None:
        return (), {}, ButtonList()
    if len(rdata) == 1:
        return rdata[0], {}, ButtonList()
    if len(rdata) == 2:
        return rdata[0], rdata[1], ButtonList()
    return rdata

def make_buttons(member: DBPlayer, callback_data: str, ignored_slot: str = None) -> ButtonList:
    buttons = []
    for slot, account in member.game_accounts.as_dict().items():
        if not account or slot == ignored_slot:
            continue
        buttons.append(InlineKeyboardButton(text=f"{account.nickname} ({account.region.upper()})", 
                                             callback_data=f"{callback_data}:{slot}"))
    return ButtonList(buttons).format_data(1)

def multi_accounts(callback_data: str, used_method: Literal["send_photo", "send_message"] = "send_message") -> Callable:
    pdb = PlayersDB()
    def wrapper(func: Callable) -> Callable:
        async def wrapper2(fself, data: 'Message', bot: 'Bot', *args, **kwargs):
            ret_data = _handle_return_data(await func(fself, data, bot=bot, *args, **kwargs))
            member = await pdb.get_member(data.from_user.id)
            if member.has_more_than_one_account:
                buttons = make_buttons(member, callback_data, member.current_game_account)
                ret_data[1]["reply_markup"] = (buttons + ret_data[2]).get_keyboard()
            return await (getattr(bot, used_method))(*ret_data[0], **ret_data[1])
        
        return wrapper2
    return wrapper
