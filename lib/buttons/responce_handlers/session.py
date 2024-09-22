import pytz
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from aiogram.types import InputMediaPhoto

from ex_func import SessionImageGenFunc
from lib.api import API
from lib.buttons import Buttons
from lib.buttons.functions import Functions
from lib.cooldown import CooldownStorage
from lib.data_classes.state_data import SessionStateData
from lib.exceptions.common.error_handler import HookExceptions
from lib.locale.locale import Text
from lib.utils import Activities

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import CallbackQuery
    from aiogram.fsm.context import FSMContext

    from lib.database.players import PlayersDB


class SessionHandlers:
    pdb: 'PlayersDB'

    @HookExceptions().hook()
    @Activities.typing
    async def session_start_session_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        try:
            state_data = (await state.get_data())["data"]
        except KeyError:
            state_data = None

        if not isinstance(state_data, SessionStateData):
            state_data = SessionStateData()
            await state.update_data({"data": state_data})
        
        await data.message.edit_text(text=Functions.session_start_text(state_data),
                                     reply_markup=Buttons.session_start_session_buttons(state_data.session_settings.is_autosession) \
                                     .get_keyboard(1),
                                     parse_mode="MarkdownV2")

    @HookExceptions().hook()
    async def session_stop_session_handle(self, data: 'CallbackQuery', **_):
        member = await self.pdb.get_member(data.from_user.id)
        await self.pdb.stop_session(member.current_slot, data.from_user.id)

        await data.message.edit_text(text=Text().get().cmds.session.sub_descr.success_stopped)
    
    @HookExceptions().hook()
    @Activities.typing
    @CooldownStorage.cooldown(10, "update_sesion")
    async def session_get_session_handle(self, data: 'CallbackQuery', bot: 'Bot', **_):
        member = await self.pdb.get_member(data.from_user.id)
        await bot.send_photo(data.message.chat.id,
                             await SessionImageGenFunc.generate_image(member.current_slot, data.from_user.id),
                             caption=datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S"),
                             reply_markup=Buttons.session_get_session_buttons().get_keyboard())
    
    @HookExceptions().hook()
    async def session_autosession_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: SessionStateData = (await state.get_data())["data"]

        is_autosession = not state_data.session_settings.is_autosession
        state_data.session_settings.is_autosession = is_autosession
        await data.message.edit_reply_markup(reply_markup=Buttons.session_start_session_buttons(is_autosession) \
                                             .get_keyboard(1))
    
    @HookExceptions().hook()
    async def session_timezone_handle(self, data: 'CallbackQuery', **_):
        await data.message.edit_reply_markup(reply_markup=Buttons.session_timezone_buttons().get_keyboard())
    
    @HookExceptions().hook()
    async def session_set_timezone_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: SessionStateData = (await state.get_data())["data"]
        timezone = int(data.data.split(":")[1])
        state_data.session_settings.timezone = timezone
        
        await Functions.session_back(data.message, state)
    
    @HookExceptions().hook()
    async def session_restart_time_handle(self, data: 'CallbackQuery', **_):
        await data.message.edit_reply_markup(reply_markup=Buttons.session_restart_time_buttons().get_keyboard())
    
    @HookExceptions().hook()
    async def session_set_restart_time_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: SessionStateData = (await state.get_data())["data"]
        restart_time = int(data.data.split(":")[1])
        state_data.session_settings.time_to_restart = datetime.now() + timedelta(hours=restart_time)
        
        await Functions.session_back(data.message, state)
    
    @HookExceptions().hook()
    async def session_fstart_session_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: SessionStateData = (await state.get_data())["data"]

        member = await self.pdb.get_member(data.from_user.id)
        account = member.current_account
        last_stats = await API().get_stats(region=account.region, game_id=account.game_id)
        await self.pdb.start_session(member.current_slot, data.from_user.id, 
                                     last_stats, state_data.session_settings)
        await data.message.edit_text(text=Text().get().cmds.session.sub_descr.success_started)
    
    @HookExceptions().hook()
    async def session_back_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: SessionStateData = (await state.get_data())["data"]

        await data.message.edit_text(text=Functions.session_start_text(state_data),
                                     reply_markup=Buttons.session_start_session_buttons(state_data.session_settings.is_autosession) \
                                     .get_keyboard(1),
                                     parse_mode="MarkdownV2")

    @HookExceptions().hook()
    @Activities.upload_photo
    @CooldownStorage.cooldown(10, "update_sesion")
    async def get_session_handle(self, data: 'CallbackQuery', **_):
        splitted_data = data.data.split(":")
        if data.from_user.id != (int(splitted_data[1]) if splitted_data[1:] else data.from_user.id):
            await data.answer(Text().get().frequent.errors.bad_button_responce)
            return
        
        member = await self.pdb.get_member(data.from_user.id)
        await data.message.edit_media(InputMediaPhoto(media=\
                                                      await SessionImageGenFunc.generate_image(member.current_slot, 
                                                                                               data.from_user.id)))
        await data.message.edit_caption(caption=datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S"),
                                        reply_markup=Buttons.get_session_buttons(data.from_user.id).get_keyboard())