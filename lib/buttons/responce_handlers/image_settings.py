import base64
from io import BytesIO
from copy import deepcopy
from typing import TYPE_CHECKING

from aiogram.types import  BufferedInputFile

from lib.settings.settings import Config
from lib.image.themes.theme_loader import get_theme

from lib.api import API
from lib.buttons import Buttons
from lib.buttons.functions import Functions
from lib.data_classes.db_player import ImageSettings
from lib.data_classes.state_data import ImageSettingsStateData
from lib.database.players import PlayersDB
from lib.exceptions.common.error_handler import HookExceptions
from lib.states import ImageSettingsStates
from lib.locale.locale import Text
from lib.image import SettingsRepresent
from lib.utils import Activities, safe_delete_message
from lib.utils.stats_preview import StatsPreview

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import CallbackQuery
    from aiogram.fsm.context import FSMContext

_config = Config().get()


class ImageSettingsHandlers:
    pdb: PlayersDB

    @HookExceptions().hook()
    async def image_settings_handle(self, query: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        await safe_delete_message(query.message)
        member_id = query.from_user.id
        member = await self.pdb.get_member(member_id)
        current_account = member.current_account
        player_global_data = await API().get_stats(current_account.region, current_account.game_id, member.current_slot)
        image_settings = await self.pdb.get_image_settings(member.current_slot, member_id, member)
        stats_preview = StatsPreview(await bot.send_photo(query.message.chat.id, 
                                                          await StatsPreview.generate_preview(member, player_global_data), 
                                                          caption=Text().get().cmds.image_settings.sub_descr.preview),
                                     member_id, member, player_global_data)
        state_data = ImageSettingsStateData(author_id=member_id, stats_preview=stats_preview, 
                                            base_image_settings=image_settings,
                                            current_image_settings=deepcopy(image_settings))
        main_message = await bot.send_photo(query.message.chat.id, 
                                            BufferedInputFile(SettingsRepresent().draw(image_settings).read(), 
                                                             "image_settings.png"),
                                            caption=Text().get().cmds.image_settings.sub_descr.main_text,
                                            reply_markup=Buttons.image_settings_buttons(state_data, True).get_keyboard(1))
        state_data.main_message = main_message
        
        await state.update_data({"data": state_data})

    @HookExceptions().hook()
    async def image_settings_back_handle(self, data: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        await Functions.image_settings_back(bot, state, data.message)                                                                                                                                                                                                                                                        
    
    @HookExceptions().hook()
    @Activities.typing
    async def image_settings_save_handle(self, data: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        image = state_data.image
        await state.update_data(data={"data": None})

        if isinstance(image, BytesIO):
            await self.pdb.set_image(
                data.from_user.id,
                base64.b64encode(image.getvalue()).decode(),
            )
        elif isinstance(image, str):
            await self.pdb.set_image(data.from_user.id)

        await self.pdb.set_image_settings((await self.pdb.get_member(data.from_user.id)).current_slot, 
                                          data.from_user.id, state_data.current_image_settings)
        await data.message.delete()
        await safe_delete_message(state_data.stats_preview.msg)
        await bot.send_message(data.message.chat.id, Text().get().cmds.image_settings.info.set_ok)
    
    @HookExceptions().hook()
    @Activities.upload_photo
    async def image_settings_reset_handle(self, __, state: 'FSMContext', bot: 'Bot', **_):
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        state_data.current_image_settings = ImageSettings.model_validate({})
        state_data.resetted = True
        await Functions.image_settings_back(bot, state)
    
    @HookExceptions().hook(del_message_on_error=True)
    @Activities.typing
    async def image_settings_bg_handle(self, data: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        await state.set_state(ImageSettingsStates.custom_bg)
        await data.message.edit_reply_markup(reply_markup=None)
        msg = await bot.send_message(data.message.chat.id, Text().get().cmds.image_settings.sub_descr.set_bg,
                                     reply_markup=Buttons.image_settings_bg_buttons(data.from_user.id).get_keyboard(1))
        (await state.get_data())['data'].delete_messages.append(msg)
    
    @HookExceptions().hook(del_message_on_error=True)
    async def image_settings_reset_bg_handle(self, data: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        state_data.image = _config.image.default_bg_path
        await Functions.image_settings_back(bot, state, data.message)
        
    
    @HookExceptions().hook(del_message_on_error=True)
    @Activities.typing
    async def image_settings_colors_handle(self, data: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        await data.message.edit_reply_markup(reply_markup=None)
        msg = await bot.send_message(data.message.chat.id, 
                                     Text().get().cmds.image_settings.sub_descr.choose_color2change,
                                     reply_markup=Buttons.image_settings_colors_buttons().get_keyboard(None))
        (await state.get_data())["data"].colors_message = msg
    
    @HookExceptions().hook(del_message_on_error=True)
    @Activities.typing
    async def image_settings_color_handle(self, data: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        await state.set_state(ImageSettingsStates.change_color)
        color_of_what = data.data.split(':')[1]
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        state_data.color_of_what = color_of_what
        colors_msg = state_data.colors_message
        await colors_msg.edit_reply_markup()
        msg = await bot.send_message(data.message.chat.id,
                                     Text().get().cmds.image_settings.sub_descr.type_new_color,
                                     reply_markup=Buttons.image_settings_colors_back_buttons().get_keyboard())
        state_data.delete_messages.append(msg)
    
    @HookExceptions().hook(del_message_on_error=True)
    async def image_settings_colors_back_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        await state.set_state()
        await data.message.delete()
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        colors_message = state_data.colors_message
        if not colors_message.reply_markup:
            await colors_message.edit_reply_markup(reply_markup=Buttons.image_settings_colors_buttons() \
                                                   .get_keyboard(None))
        await state_data.delete_messages.clear()
    
    @HookExceptions().hook(del_message_on_error=True)
    async def image_settings_other_handle(self, data: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        await data.message.edit_reply_markup(reply_markup=None)
        msg = await bot.send_message(data.message.chat.id, 
                                     Text().get().cmds.image_settings.sub_descr.choose_param2change,
                                     reply_markup=Buttons.image_settings_other_buttons().get_keyboard(None))
        (await state.get_data())["data"].others_message = msg
    
    @HookExceptions().hook(del_message_on_error=True)
    async def image_settings_other_back_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        await state_data.delete_messages.clear()
        await Functions.image_settings_other_back(state_data.others_message)
    
    @HookExceptions().hook(del_message_on_error=True)
    async def image_settings_other_param_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        param_name = data.data.split(':')[1]
        (await state.get_data())["data"].other_change_param = param_name
        await data.message.edit_text(getattr(Text().get().cmds.image_settings.descr.sub_descr, param_name),
                                     reply_markup=Buttons.image_settings_other_onoff_buttons().get_keyboard(2))
    
    @HookExceptions().hook(del_message_on_error=True)
    async def image_settings_other_on_off_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        param_name = state_data.other_change_param
        change2 = not not int(data.data.split(":")[1])
        setattr(state_data.current_image_settings, param_name, change2)
        await data.answer(Text().get().frequent.info.good_button_respoce)
        await Functions.image_settings_other_back(data.message)
    
    @HookExceptions().hook(del_message_on_error=True)
    async def image_settings_other_glass_effect_handle(self, data: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        await state.set_state(ImageSettingsStates.glass_effect)
        await data.message.edit_reply_markup()
        
        msg = await bot.send_message(data.message.chat.id, Text().get().cmds.image_settings.sub_descr.glass_effect,
                                     reply_markup=Buttons.image_settings_other_back_buttons().get_keyboard())
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        state_data.delete_messages.append(msg)
        state_data.others_message = data.message
    
    @HookExceptions().hook(del_message_on_error=True)
    async def image_settings_other_blocks_bg_brightness_handle(self, data: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        await state.set_state(ImageSettingsStates.blocks_bg_brightness)
        await data.message.edit_reply_markup()
        
        msg = await bot.send_message(data.message.chat.id, 
                                     Text().get().cmds.image_settings.descr.sub_descr.stats_blocks_transparency,
                                     reply_markup=Buttons.image_settings_other_back_buttons().get_keyboard())
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        state_data.delete_messages.append(msg)
        state_data.others_message = data.message
    
    @HookExceptions().hook(del_message_on_error=True)
    async def image_settings_theme_handle(self, data: 'CallbackQuery', bot: 'Bot', **_):
        await data.message.edit_reply_markup()
        await bot.send_message(data.message.chat.id, Text().get().cmds.image_settings.sub_descr.available_themes,
                               reply_markup=Buttons.image_settings_theme_buttons().get_keyboard(None))
    
    @HookExceptions().hook(del_message_on_error=True)
    async def image_settings_theme_set_handle(self, data: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        theme_name = data.data.split(":")[1]
        theme = get_theme(theme_name)
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        current_image_settings = state_data.current_image_settings
        
        for changing_param_name in ["theme", "colorize_stats", "stats_blocks_transparency", "glass_effect",
                                    "nickname_color", "clan_tag_color", "stats_color", "main_text_color",
                                    "stats_text_color", "negative_stats_color", "positive_stats_color"]:
            setattr(current_image_settings, changing_param_name, getattr(theme.image_settings, changing_param_name))

        await Functions.image_settings_back(bot, state, data.message)
