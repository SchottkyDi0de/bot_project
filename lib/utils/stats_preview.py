from io import BytesIO
from copy import deepcopy
from typing import TYPE_CHECKING

from aiogram.types import BufferedInputFile, InputMediaPhoto
from aiogram.enums import ChatAction

from lib.data_parser.parse_data import get_session_stats

from lib.api import API
from lib.image import CommonImageGen, SessionImageGen
from lib.locale.locale import Text

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message
    from aiogram.fsm.context import FSMContext

    from lib.data_classes.api.api_data import PlayerGlobalData

    from lib.data_classes.db_player import DBPlayer, ImageSettings


class StatsPreview:
    def __init__(self, msg: 'Message', author_id: int, player: 'DBPlayer', player_global_data: 'PlayerGlobalData'):
        self.player = player
        self.account = self.player.current_account
        self.author_id = author_id
        self.player_global_data = player_global_data
        self.msg = msg
        self.img_gen = CommonImageGen()
    
    @staticmethod
    async def generate_preview(member: 'DBPlayer', player_global_data: 'PlayerGlobalData | None' = None) -> BufferedInputFile:
        account = member.current_account
        if not player_global_data:
            player_global_data = await API().get_stats(account.region, account.game_id, member.current_slot)
        img = CommonImageGen().generate(player_global_data, member, member.current_slot)
        return BufferedInputFile(img.read(), "preview.png")
    
    async def update_preview(self, bot: 'Bot', state: 'FSMContext'):
        data = (await state.get_data())["data"]     #ImageSettingsStateData
        base_image_settings: 'ImageSettings' = data.base_image_settings
        current_image_settings: 'ImageSettings' = data.current_image_settings
        lgis_temp: 'ImageSettings' = data.last_generated_image_settings
        last_generated_image_settings = lgis_temp if lgis_temp else base_image_settings
        image = data.image
        is_changed = base_image_settings != current_image_settings or (not not image)
        data.is_changed = is_changed
        need_regenerate = (last_generated_image_settings != current_image_settings \
            or ((not not image) and current_image_settings.theme == "default"))

        if need_regenerate:
            await bot.send_chat_action(self.msg.chat.id, ChatAction.UPLOAD_PHOTO)
            img = self.img_gen.generate(self.player_global_data, self.player, self.player.current_slot,
                                        force_image_settings=current_image_settings, force_image=image)
            await self.msg.edit_media(InputMediaPhoto(media=BufferedInputFile(img.read(),
                                                                              "preview.png")))
            await self.msg.edit_caption(caption=Text().get().cmds.image_settings.sub_descr.preview)
            data.last_generated_image_settings = deepcopy(current_image_settings)
            if isinstance(image, BytesIO):
                image.seek(0)


class SVPreview:
    def __init__(self, msg: 'Message', player: 'DBPlayer', player_global_data: 'PlayerGlobalData'):
        self.msg = msg
        self.player = player
        self.diff_data = None
        self.player_global_data = player_global_data
        
    @staticmethod
    async def generate_preview(member: 'DBPlayer', player_global_data: 'PlayerGlobalData | None' = None) -> BufferedInputFile:
        account = member.current_account
        if not player_global_data:
            player_global_data = await API().get_stats(account.region, account.game_id, member.current_slot)
        diff_data = await get_session_stats(player_global_data, player_global_data, zero_bypass=True)
        img = SessionImageGen().generate(player_global_data, diff_data, member, member.current_slot)
        return BufferedInputFile(img.read(), "preview.png")
    
    async def update_preview(self, bot: 'Bot', state: 'FSMContext'):
        data = (await state.get_data())["data"]     

        if self.diff_data is None:
            diff_data = await get_session_stats(self.player_global_data, self.player_global_data, zero_bypass=True)
            diff_data.main_diff.battles = 1
            self.diff_data = diff_data
        
        self.diff_data.rating_diff.battles = int(data.rating)

        if data.need_regenerate:
            image = SessionImageGen().generate(self.player_global_data, 
                                               self.diff_data, 
                                               self.player, 
                                               self.player.current_slot,
                                               force_stats_view=data.current_sv_settings)
            await self.msg.edit_media(InputMediaPhoto(media=BufferedInputFile(image.read(), "preview.png")))
