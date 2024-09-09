from copy import deepcopy
from typing import TYPE_CHECKING

from lib.utils.string_parser import insert_data

from lib.database.players import PlayersDB
from lib.data_classes.db_player import WidgetSettings
from lib.data_classes.state_data import WidgetSettingsStateData
from lib.states import SessionWidgetStates
from lib.exceptions.common import HookExceptions
from lib.locale.locale import Text
from lib.validators import get_validator_by_name
from lib.utils import safe_delete_message, jsonify
from workers import AutoDeleteMessage

from ..buttons import Buttons
from ..functions import Functions

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import CallbackQuery
    from aiogram.fsm.context import FSMContext


class SessionWidgetHandlers:
    pdb: PlayersDB

    @HookExceptions().hook()
    async def session_widget_handle(self, query: 'CallbackQuery', bot: 'Bot', state: 'FSMContext', **_):
        await safe_delete_message(query.message)
        member = await self.pdb.get_member(query.from_user.id)
        account = member.current_account
        state_data = WidgetSettingsStateData(base_widget_settings=deepcopy(account.widget_settings),
                                            current_widget_settings=deepcopy(account.widget_settings))
        await state.update_data({"data": state_data})
        if account.widget_settings.is_default:
            msg = await bot.send_message(query.message.chat.id, Text().get().cmds.session_widget.settings.edit.descr,
                                         reply_markup=Buttons.session_widget_settings_edit_buttons(state_data).get_keyboard(1))
        else:
            msg = await bot.send_message(query.message.chat.id, 
                                         insert_data(Text().get().cmds.session_widget.settings.descr,
                                                     {"settings": jsonify(Text().get().cmds.session_widget.settings.buttons.edit_buttons, 
                                                                          account.widget_settings.model_dump())}), 
                                         reply_markup=Buttons.session_widget_settings_buttons(state_data).get_keyboard(1),
                                         parse_mode="MarkdownV2")
        state_data.main_message = msg
    
    @HookExceptions().hook()
    async def session_widget_settings_edit_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: WidgetSettingsStateData = (await state.get_data())["data"]
        
        await data.message.edit_text(text=Text().get().cmds.session_widget.settings.edit.descr,
                                     reply_markup=Buttons.session_widget_settings_edit_buttons(state_data).get_keyboard(1))
        
    @HookExceptions().hook()
    async def session_widget_settings_save_handle(self, data: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        state_data: WidgetSettingsStateData = (await state.get_data())["data"]
        member = await self.pdb.get_member(data.from_user.id)

        await state.update_data(data={"data": None})
        await self.pdb.set_widget_settings(member.current_slot, 
                                           data.from_user.id, 
                                           state_data.current_widget_settings)
        await data.message.delete()
        await bot.send_message(data.message.chat.id, Text().get().cmds.session_widget.settings.info.success)

    @HookExceptions().hook()
    async def session_widget_settings_reset_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: WidgetSettingsStateData = (await state.get_data())["data"]

        state_data.current_widget_settings = WidgetSettings()
        state_data.resetted = True
        await Functions.session_widget_back(data.message, state)
    
    @HookExceptions().hook()
    async def session_widget_settings_back_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        await Functions.session_widget_back(data.message, state)
    
    @HookExceptions().hook()
    async def session_widget_settings_edit_io_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: WidgetSettingsStateData = (await state.get_data())["data"]

        state_data.changing_param_name = data.data.split(":")[1]
        await state.set_state(SessionWidgetStates.io)

        param_name = getattr(Text().get().cmds.session_widget.settings.buttons.edit_buttons, 
                             state_data.changing_param_name)
        validator = get_validator_by_name(state_data.changing_param_name, return_object=True)
        await data.message.edit_text(
            text=insert_data(Text().get().cmds.session_widget.settings.edit.io_change, 
                             {"param": param_name, 
                              "limits": validator.limits}),
            reply_markup=Buttons.session_widget_settings_edit_back_buttons().get_keyboard(1)
            )
    
    @HookExceptions().hook()
    async def session_widget_settings_edit_back_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        await state.set_state()
        (await state.get_data())["data"].changing_param_name = None

        await data.message.edit_text(
            text=Text().get().cmds.session_widget.settings.edit.descr,
            reply_markup=Buttons.session_widget_settings_edit_buttons((await state.get_data())["data"]).get_keyboard(1)
        )

    @HookExceptions().hook()
    async def session_widget_settings_edit_bool_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: WidgetSettingsStateData = (await state.get_data())["data"]
        ch_param = data.data.split(":")[1]
        state_data.changing_param_name = ch_param

        keyboard = Buttons.session_widget_settings_edit_onoff_buttons().format_data(2)
        keyboard.extend(Buttons.session_widget_settings_edit_back_buttons().format_data(1))

        await data.message.edit_text(text=insert_data(Text().get().cmds.session_widget.settings.edit.bool_change, 
                                                      {"param": getattr(Text().get().cmds.session_widget.settings.buttons.edit_buttons, 
                                                                        ch_param)}),
                                     reply_markup=keyboard.get_keyboard())
    
    @HookExceptions().hook()
    async def session_widget_settings_edit_onoff_handle(self, data: 'CallbackQuery', bot: 'Bot', state: 'FSMContext', **_):
        state_data: WidgetSettingsStateData = (await state.get_data())["data"]
        
        set_to = data.data.split(":")[1] == "1"
        setattr(state_data.current_widget_settings, state_data.changing_param_name, set_to)

        AutoDeleteMessage.add2list(await bot.send_message(data.message.chat.id,
                                                          Text().get().cmds.session_widget.settings.edit.success_onoff),
                                   5)
        
        await Functions.session_widget_back(data.message, state)
