from typing import TYPE_CHECKING


from lib.utils.string_parser import insert_data

from extensions.setup import ExtensionsSetup
from lib import HookExceptions, SessionWidgetStates, Text, get_validator_by_name
from lib.buttons.functions import Functions
from workers import AutoDeleteMessage

if TYPE_CHECKING:
    from aiogram.types import Message
    from aiogram.fsm.context import FSMContext
    
    from lib.data_classes.state_data import WidgetSettingsStateData



class SessionWidgetSettings(ExtensionsSetup):
    __funcs_filters__ = [
        ("session_widget_settings_edit_io", (SessionWidgetStates.io,))
    ]

    @HookExceptions().hook()
    async def session_widget_settings_edit_io(self, msg: 'Message', state: 'FSMContext', **_):
        state_data: 'WidgetSettingsStateData' = (await state.get_data())["data"]

        idata = msg.text.strip()
        validator = get_validator_by_name(state_data.changing_param_name)
        validator_obj = validator(idata)
        
        if not validator_obj.validate():
            AutoDeleteMessage.add2list(msg, 5)
            AutoDeleteMessage.add2list(await msg.reply("👎"), 5)
            return

        param_name = state_data.changing_param_name
        pr_data = validator_obj.post_procces()
        setattr(state_data.current_widget_settings, param_name, pr_data)
        await state.set_state()
        l_param_name = getattr(Text().get().cmds.session_widget.settings.buttons.edit_buttons, param_name)

        await msg.reply(insert_data(
            Text().get().cmds.session_widget.settings.edit.io_success,
            {"param": l_param_name, "value": idata}
            ))
        
        await Functions.session_widget_back(state_data.main_message, state)
