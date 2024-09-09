from typing import TYPE_CHECKING

from aiogram.types import BufferedInputFile, InputMediaPhoto

from ex_func import StatsFunc
from lib.buttons.utils.mulacc_buttons import make_buttons
from lib.cooldown import CooldownStorage
from lib.database.players import PlayersDB
from lib.data_classes.db_player import AccountSlotsEnum
from lib.exceptions.common import HookExceptions
from lib.utils import Activities

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery


class StatsHandlers:
    pdb: PlayersDB

    @HookExceptions().hook()
    @Activities.typing
    @CooldownStorage.cooldown(10, "gen_stats")
    async def stats_macc_handle(self, data: 'CallbackQuery', **_):
        slot = AccountSlotsEnum[data.data.split(':')[1]]
        member = await self.pdb.get_member(data.from_user.id)
        rdata = await StatsFunc.stats4registred_player(slot, member)

        if isinstance(rdata, str):
            await data.answer(rdata)
        
        await data.message.edit_media(InputMediaPhoto(media=BufferedInputFile(rdata.read(), "stats.png")),
                                      reply_markup=make_buttons(member, "stats_macc", slot.name).get_keyboard(1))
