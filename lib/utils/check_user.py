from typing import TYPE_CHECKING, Callable

from lib.locale.locale import Text
from lib.settings import Config
from lib.database.players import PlayersDB
from lib.database.internal import InternalDB

if TYPE_CHECKING:
    from aiogram.types import Message, CallbackQuery

_config = Config().config


def check(
        is_banned: bool=True, 
        in_db: bool=True, 
        private_only: bool=False, 
        has_premium: bool=False,
        developer_only: bool=False
          ) -> Callable:
    pdb = PlayersDB()
    idb = InternalDB()

    def inner(func: Callable) -> Callable:
        async def wrapper(self, data: 'Message | CallbackQuery', *args, **kwargs):
            from_user = data.from_user

            if is_banned:
                if await idb.check_ban(from_user.id):
                    return
            if developer_only:
                if from_user.id not in _config.developers_id:
                    return
            if in_db:
                if not await pdb.check_member_exists(from_user.id, raise_error=False):
                    await data.reply(Text().get().frequent.info.unregistred_player)
                    return
            if private_only:
                if data.chat.type != 'private':
                    await data.reply(Text().get().frequent.info.is_channel)
                    return
            if has_premium:
                ...
#                if await pdb.check_premium(from_user.id):
#                    await data.reply(Text().get().frequent.info.premium_only)
#                    return
            return await func(self, data, *args, **kwargs)
        return wrapper
    return inner