from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.types import BufferedInputFile

from lib.utils.string_parser import insert_data

from lib.exceptions.common import HookExceptions
from lib.locale.locale import Text
from lib.database.players import PlayersDB
from lib.data_classes.db_player import AccountSlotsEnum
from lib.buttons.utils.mulacc_buttons import make_buttons
from lib.image.profile import ProfileImageGen

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery


class ProfileResponces:
    pdb: PlayersDB

    @HookExceptions().hook()
    async def profile_settings_handle(self, data: 'CallbackQuery', bot: 'Bot', **_):
        msg = data.message
        usrname = data.from_user.username
        member = await self.pdb.get_member(data.from_user.id)
        account = member.current_account
        await msg.delete()
        profile_image = ProfileImageGen().generate(member, usrname if usrname else data.from_user.id)
        buffered_file = BufferedInputFile(profile_image.read(), "profile.png")

        await bot.send_photo(msg.chat.id, buffered_file, 
                             caption=insert_data(Text().get().cmds.settings.sub_descr.profile_text,
                                                 {"nickname": account.nickname, "region": account.region}),
                             reply_markup=make_buttons(member, "profile_curr_change", member.current_game_account) \
                                .get_keyboard())
    
    @HookExceptions().hook()
    async def profile_curr_change_handle(self, data: 'CallbackQuery', **_):
        text_slot = data.data.split(":")[-1]
        new_slot = AccountSlotsEnum[text_slot]
        await self.pdb.set_current_account(data.from_user.id, new_slot, validate=False)
        member = await self.pdb.get_member(data.from_user.id)
        current_account = member.game_accounts.get_account_by_slot(new_slot)
        await data.message.edit_caption(caption=insert_data(Text().get().cmds.settings.sub_descr \
                                                                .profile_switch_success,
                                                            {"nickname": current_account.nickname,
                                                             "region": current_account.region}))
