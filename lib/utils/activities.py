from typing import TYPE_CHECKING, Callable

from aiogram.types import Message
from aiogram.enums import ChatAction

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import CallbackQuery


class Activities:   #я конечно знаю про aiogram.flags, но как по мне, с моим вариантом лучше выглядит
    def typing(func: Callable) -> Callable:
        async def wrapper(fself, data: 'Message | CallbackQuery', bot: 'Bot', *args, **kwargs):
            chat_id = data.chat.id if isinstance(data, Message) else data.message.chat.id
            await bot.send_chat_action(chat_id, ChatAction.TYPING)
            return await func(fself, data, bot=bot, *args, **kwargs)
        return wrapper

    def upload_photo(func: Callable) -> Callable:
        async def wrapper(fself, data: 'Message | CallbackQuery', bot: 'Bot', *args, **kwargs):
            chat_id = data.chat.id if isinstance(data, Message) else data.message.chat.id
            await bot.send_chat_action(chat_id, ChatAction.UPLOAD_PHOTO)
            return await func(fself, data, bot=bot, *args, **kwargs)
        return wrapper
