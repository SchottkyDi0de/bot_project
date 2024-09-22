from typing import TYPE_CHECKING

from lib.settings.settings import Config
from lib.data_classes.api.api_data import PlayerGlobalData
from lib.utils.string_parser import insert_data

from lib.api import API
from lib.locale.locale import Text
from lib.buttons import Buttons
from lib.buttons.functions import Functions
from lib.states import HookStates
from lib.cooldown import CooldownStorage
from lib.exceptions.common import HookExceptions
from lib.database.players import PlayersDB
from lib.data_classes.db_player import HookStats

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery
    from aiogram.fsm.context import FSMContext

_config = Config().get()


def _get_target_stats(data: PlayerGlobalData, stats_type: str, stats_name: str):
    stats = getattr(data.data.statistics, "all" if stats_type == "common" else "rating")
    return getattr(stats, stats_name)


class HookHandlers:
    api: API
    pdb: PlayersDB
    
    @HookExceptions().hook()
    async def new_hook_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        await Functions.new_hook(data.message, state)

    @HookExceptions().hook()
    async def hook_region_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: HookStats = (await state.get_data())["data"]

        state_data.target_region = data.data.split(":")[1]
        await state.set_state(HookStates.target_nickname)
        await data.message.edit_text(Text().get().cmds.hook.sub_descr.type_nickname)
    
    @HookExceptions().hook()
    async def hook_rating_param_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: HookStats = (await state.get_data())["data"]

        inpd = not not int(data.data.split(":")[1])
        if inpd:
            state_data.stats_type = "rating"
            markup = Buttons.hook_rating_buttons().format_data(3)
            markup += Buttons.hook_rating_onoff_buttons(True).format_data(1)
        else:
            state_data.stats_type = "common"
            markup = Buttons.hook_target_stats_buttons().format_data(3)
            markup += Buttons.hook_rating_onoff_buttons(False).format_data(1)
        
        await data.message.edit_reply_markup(reply_markup=markup.get_keyboard())
    
    @HookExceptions().hook()
    async def hook_target_stats_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: HookStats = (await state.get_data())["data"]

        state_data.stats_name = data.data.split(":")[1]
        await data.message.edit_text(text=Text().get().cmds.hook.sub_descr.choose_trigger, 
                                     reply_markup=Buttons.hook_target_trigger_buttons().get_keyboard(1))
    
    @HookExceptions().hook()
    async def hook_target_trigger_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: HookStats = (await state.get_data())["data"]

        state_data.trigger = data.data.split(":")[1]
        await data.message.edit_text(text=Text().get().cmds.hook.sub_descr.type_value)
        await state.set_state(HookStates.target_value)
    
    @HookExceptions().hook()
    async def hook_watch_for_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: HookStats = (await state.get_data())["data"]

        state_data.watch_for = data.data.split(":")[1]
        state_data.active = True
        state_data.hook_target_chat_id = data.message.chat.id
        state_data.hook_target_member_id = data.from_user.id
        lang = data.from_user.language_code[:2]
        lang = lang if lang in _config.default.available_locales else _config.default.lang
        state_data.lang = lang

        await self.pdb.setup_stats_hook(data.from_user.id, state_data)
        await data.message.edit_text(text=Text().get().cmds.hook.info.activated)
    
    @HookExceptions().hook()
    @CooldownStorage.cooldown(10)
    async def hook_state_handle(self, data: 'CallbackQuery', **_):
        member = await self.pdb.get_member(data.from_user.id)
        hook = member.hook_stats

        starting_value = _get_target_stats(hook.last_stats, hook.stats_type, hook.stats_name)
        current_value = _get_target_stats(await self.api.get_stats(region=hook.target_region, 
                                                                   game_id=hook.last_stats.id), 
                                          hook.stats_type, 
                                          hook.stats_name)
        text = insert_data(Text().get().cmds.hook.sub_descr.hook_state, {
            "nickname": hook.last_stats.nickname,
            "region": hook.last_stats.region,
            "starting_value": f"{starting_value:.2f}",
            "current_value": f"{current_value:.2f}",
            "time_left": hook.end_time.strftime("%H:%M:%S"),
            **{key: getattr(hook, key) for key in ["stats_type", "trigger", "target_value", "watch_for"]},
        })
        await data.message.edit_text(text=text, parse_mode="MarkdownV2")
    
    @HookExceptions().hook()
    async def disable_hook_handle(self, data: 'CallbackQuery', **_):
        await self.pdb.disable_stats_hook(data.from_user.id)
        await data.message.edit_text(Text().get().cmds.hook.info.disabled)
