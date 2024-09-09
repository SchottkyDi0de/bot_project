from io import BytesIO
from typing import TYPE_CHECKING

from aiogram import F
from aiogram.types import ReactionTypeEmoji
from aiogram.filters import or_f

from PIL import Image

from lib.image.utils.resizer import resize_image
from lib.image.utils.color_validator import RawRegex, color_validate

from extensions.setup import ExtensionsSetup
from lib import (Buttons, HookExceptions, ImageSettingsStateData, ImageSettingsStates,
                    PlayersDB, Text, Activities, safe_delete_message, rgb2hex)
from lib.buttons.functions import Functions
from workers import AutoDeleteMessage

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message
    from aiogram.fsm.context import FSMContext


class Customization(ExtensionsSetup):
    __funcs_filters__ = [
        ("image_set_handler", (ImageSettingsStates.custom_bg,)),
        (
            "image_color_set_handler", 
            (or_f(F.text.regexp(RawRegex.hex), F.text.regexp(RawRegex.rgb)), 
            ImageSettingsStates.change_color)
            ),
        ("invalid_color", (ImageSettingsStates.change_color,)),
        ("image_set_glass_effect", (ImageSettingsStates.glass_effect,)),
        ("image_set_blocks_bg_brightness", (ImageSettingsStates.blocks_bg_brightness,))
    ]

    def init(self):
        self.pdb = PlayersDB()
    
    @HookExceptions().hook()
    async def image_set_handler(self, msg: 'Message', state: 'FSMContext', bot: 'Bot', **_):
        try:
            photo = msg.photo[-1]
        except TypeError:
            await bot.set_message_reaction(msg.chat.id, msg.message_id, [ReactionTypeEmoji(emoji="👎")])
            return
        
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        incorrect = False

        if photo.file_size > 2_097_152:
            text = Text().get().cmds.image_settings.items.background.oversize
            incorrect = True
        elif photo.width < 256 or photo.height < 256:
            text = Text().get().cmds.image_settings.items.background.small_resolution
            incorrect = True
        
        if incorrect:
            await bot.send_message(msg.chat.id, f"{text}\n{Text().get().frequent.info.try_again}")
            return
        
        for photo in msg.photo[::-1]:
            if photo.width > 2048 or photo.height > 2048:
                continue
            break
        
        with await bot.download(photo.file_id, BytesIO()) as buffer:
            buffer.seek(0)
            pil_image = Image.open(buffer)
            if pil_image.format not in ["PNG", "JPG", "JPEG"]:
                await bot.send_message(msg.chat.id, f"{Text().get().frequent.errors.wrong_file_type}\n"
                                       f"{Text().get().frequent.info.try_again}")
                return
            pil_image = pil_image.convert('RGBA')
            pil_image = resize_image(pil_image, (800, 1350))

        buffer = BytesIO()
        pil_image.save(buffer, format='PNG')
        buffer.seek(0)
        state_data.image = buffer

        await bot.set_message_reaction(msg.chat.id, msg.message_id, [ReactionTypeEmoji(emoji="👍")])
        await Functions.image_settings_back(bot, state)
        await state_data.delete_messages.clear()

    @HookExceptions().hook()
    async def image_color_set_handler(self, msg: 'Message', state: 'FSMContext', bot: 'Bot', **_):
        await state.set_state()
        _match, _type = color_validate(msg.text)
        if _type == "rgb":
            _hex = rgb2hex(_match)
        else:
            _hex = msg.text
        
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        setattr(state_data.current_image_settings, state_data.color_of_what, _hex)
        colors_message: 'Message' = state_data.colors_message
        await colors_message.edit_reply_markup(reply_markup=Buttons.image_settings_colors_buttons().get_keyboard(None))
        await state_data.delete_messages.clear()
        await safe_delete_message(msg)
        AutoDeleteMessage.add2list(await bot.send_message(msg.chat.id, "👍"), 5)
    
    @HookExceptions().hook()
    @Activities.typing
    async def invalid_color(self, msg: 'Message', state: 'FSMContext', bot: 'Bot', **_):
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        state_data.delete_messages + msg
        state_data.delete_messages + await bot.send_message(msg.chat.id, 
                                                            Text().get().cmds.image_settings.items.color_error_footer + \
                                                            '\n' + Text().get().frequent.info.try_again)

    @HookExceptions().hook()
    @Activities.typing
    async def image_set_glass_effect(self, msg: 'Message', state: 'FSMContext', bot: 'Bot', **_):
        state_data: ImageSettingsStateData = (await state.get_data())["data"]

        try:
            glass_effect = int(msg.text.strip())
        except TypeError:
            await bot.set_message_reaction(msg.chat.id, msg.message_id, [ReactionTypeEmoji(emoji="👎")])
            state_data.delete_messages + msg
            return
        
        if not (0 <= glass_effect <= 30):
            await bot.set_message_reaction(msg.chat.id, msg.message_id, [ReactionTypeEmoji(emoji="👎")])
            state_data.delete_messages + msg
            return

        state_data.current_image_settings.glass_effect = glass_effect
        await state.set_state()
        
        await state_data.delete_messages.clear()
        await Functions.image_settings_other_back(state_data.others_message)

        AutoDeleteMessage.add2list(msg, 5)
        AutoDeleteMessage.add2list(await bot.send_message(msg.chat.id, "👍"), 5)
    
    @HookExceptions().hook()
    @Activities.typing
    async def image_set_blocks_bg_brightness(self, msg: 'Message', state: 'FSMContext', bot: 'Bot', **_):
        state_data: ImageSettingsStateData = (await state.get_data())["data"]
        brightness = 0
        err = False

        try:
            brightness = int(msg.text.strip())
        except TypeError:
            err = True
        
        if not (0 <= brightness <= 100):
            err = True
        
        if err:
            await bot.set_message_reaction(msg.chat.id, msg.message_id, [ReactionTypeEmoji(emoji="👎")])
            state_data.delete_messages + msg
            return

        state_data.current_image_settings.stats_blocks_transparency = brightness / 100
        await state.set_state()
        
        await state_data.delete_messages.clear()
        await Functions.image_settings_other_back(state_data.others_message)

        AutoDeleteMessage.add2list(msg, 5)
        AutoDeleteMessage.add2list(await bot.send_message(msg.chat.id, "👍"), 5)
