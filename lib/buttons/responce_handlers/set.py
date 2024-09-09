from typing import TYPE_CHECKING


from lib.database.players import PlayersDB
from lib.data_classes.db_player import AccountSlotsEnum
from lib.exceptions.common.error_handler import HookExceptions
from lib.locale.locale import Text
from lib.states import SetPlayerStates

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import CallbackQuery
    from aiogram.fsm.context import FSMContext


class SetHandlers:
    pdb: PlayersDB
    bot: 'Bot'

    @HookExceptions().hook(del_message_on_error=True)
    async def set_lang_handle(self, data: 'CallbackQuery', **_):

        await self.pdb.set_lang(data.from_user.id, data.data.split(':')[1])
        Text().load(data.data.split(':')[1])

        await data.message.edit_text(Text().get().cmds.set_lang.info.set_lang_ok)
    
    @HookExceptions().hook()
    async def set_player_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        region = data.data.split(':')[1]

        await state.update_data({"data": {"region": region}})
        await state.set_state(SetPlayerStates.set_nick)

        await data.message.edit_reply_markup(reply_markup=None)
        await data.message.edit_text(Text().get().cmds.set_player.info.choosed_region + f"`{region}`",
                                     parse_mode="Markdown")
        await self.bot.send_message(data.message.chat.id, Text().get().cmds.set_player.sub_descr.get_nickname)
    
    @HookExceptions().hook()
    async def sp_choose_slot_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        player = (await state.get_data())["data"]
        slot = AccountSlotsEnum[data.data.split(':')[1]]

        await self.pdb.set_member(slot, data.from_user.id, player, slot_override=True)

        await data.message.delete()
        await self.bot.send_message(data.message.chat.id, Text().get().cmds.set_player.info.set_player_ok)
