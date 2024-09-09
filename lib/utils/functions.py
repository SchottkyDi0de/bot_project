from re import Match
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiogram.types import Message


async def safe_delete_message(msg: 'Message') -> None:        
        try:
            await msg.delete()
        except Exception:
            ...


def split_list2chunks(lst: list[Any], chunk_size: int) -> list[list[Any]]:
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def rgb2hex(match: Match) -> str:
    return f"#{int(match.group(1)):02x}{int(match.group(2)):02x}{int(match.group(3)):02x}"
