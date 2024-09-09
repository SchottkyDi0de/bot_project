from copy import deepcopy
from typing import TYPE_CHECKING

from aiogram import Bot

from lib.buttons import Buttons
from lib.exceptions.common import HookExceptions
from lib.database.players import PlayersDB
from lib.data_classes.state_data import SVSettingsStateData
from lib.locale.locale import Text
from lib.utils import safe_delete_message
from lib.utils.stats_preview import SVPreview

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery
    from aiogram.fsm.context import FSMContext

    from lib.data_classes.state_data import ImageSettingsStateData


class SVSettingsHandlers:
    pdb: PlayersDB
    @HookExceptions().hook()
    async def sv_settings_handle(self, query: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        data: ImageSettingsStateData = (await state.get_data())["data"]
        for msg in [data.main_message, data.stats_preview.msg]:
            await safe_delete_message(msg)

        last_stats = data.stats_preview.player_global_data
        member = await self.pdb.get_member(query.from_user.id)
        current_account = member.current_account
        sv_settings = current_account.stats_view_settings

        preview_image = await SVPreview.generate_preview(member, last_stats)
        preview = SVPreview(await bot.send_photo(query.message.chat.id, preview_image, 
                                                 caption=Text().get().cmds.stats_view_settings.sub_descr.preview_text),
                            member, 
                            last_stats)
        state_data = SVSettingsStateData(base_sv_settings=sv_settings, current_sv_settings=deepcopy(sv_settings),
                                         preview=preview)
        await state.update_data({"data": state_data})
        await bot.send_message(query.message.chat.id, Text().get().cmds.stats_view_settings.descr.mtext,
                               reply_markup=Buttons.sv_settings_buttons(state_data).get_keyboard(1))
        
    @HookExceptions().hook()
    async def sv_settings_rating_handle(self, query: 'CallbackQuery', state: 'FSMContext', **_):
        data: SVSettingsStateData = (await state.get_data())["data"]
        data.rating = not data.rating
        await query.message.edit_reply_markup(reply_markup=Buttons.sv_settings_buttons(data).get_keyboard(1))
    
    @HookExceptions().hook()
    async def sv_settings_slot_handle(self, query: 'CallbackQuery', state: 'FSMContext', **_):
        data: SVSettingsStateData = (await state.get_data())["data"]
        data.slot_num = int(query.data.split(":")[1])
        
        await query.message.edit_reply_markup(reply_markup=Buttons.sv_settings_slot_buttons(data.rating).get_keyboard(3))
    
    @HookExceptions().hook()
    async def sv_settings_slot_set_handle(self, query: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        data: SVSettingsStateData = (await state.get_data())["data"]
        
        tstats = query.data.split(":")[1]
        getattr(data.current_sv_settings, f"{'rating' if data.rating else 'common'}_slots")[f"slot_{data.slot_num}"] = tstats
        await data.preview.update_preview(bot, state)
        await query.message.edit_reply_markup(reply_markup=Buttons.sv_settings_buttons(data).get_keyboard(1))

    @HookExceptions().hook()
    async def sv_settings_save_handle(self, query: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        data: SVSettingsStateData = (await state.get_data())["data"]

        member = await self.pdb.get_member(query.from_user.id)
        await self.pdb.set_stats_view_settings(member.current_account, query.from_user.id, data.current_sv_settings)
        await safe_delete_message(data.preview.msg)

        await query.message.edit_text(Text().get().cmds.stats_view_settings.descr.success)
