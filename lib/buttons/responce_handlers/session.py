import pytz
from datetime import datetime
from typing import TYPE_CHECKING

from aiogram.types import InputMediaPhoto

from ex_func import SessionImageGenFunc
from lib.buttons import Buttons
from lib.cooldown import CooldownStorage
from lib.database.players import PlayersDB
from lib.exceptions.common.error_handler import HookExceptions
from lib.locale.locale import Text
from lib.utils import Activities

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery


class SessionHandlers:
    pdb: PlayersDB

    @HookExceptions().hook()
    @Activities.upload_photo
    @CooldownStorage.cooldown(10, "update_sesion")
    async def get_session_handle(self, data: 'CallbackQuery', **_):
        if data.from_user.id != int(data.data.split(":")[1]):
            await data.answer(Text().get().frequent.errors.bad_button_responce)
            return
        
        member = await self.pdb.get_member(data.from_user.id)
        await data.message.edit_media(InputMediaPhoto(media=\
                                                      await SessionImageGenFunc.generate_image(member.current_slot, 
                                                                                               data.from_user.id)))
        await data.message.edit_caption(caption=datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S"),
                                        reply_markup=Buttons.get_session_buttons(data.from_user.id).get_keyboard())