from typing import TYPE_CHECKING

from aiogram import F
from aiogram.filters import Command

from lib.logger.logger import get_logger
from lib.utils.validators import validate, RawRegex
from lib.utils.nickname_handler import handle_nickname

from extensions.setup import ExtensionsSetup
from lib.api.async_wotb_api import API
from lib.buttons import Buttons
from lib.exceptions.common.error_handler import HookExceptions
from lib.database.players import PlayersDB
from lib.data_classes.db_player import AccountSlotsEnum
from lib.locale.locale import Text
from lib.states import SetPlayerStates
from lib.utils import Activities, analytics, parse_message
from lib.utils.check_user import check

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message
    from aiogram.fsm.context import FSMContext

    from lib.data_classes.db_player import GameAccount


_log = get_logger(__file__, 'TgSetLogger', 'logs/tg_set.log')


class Set(ExtensionsSetup):
    __funcs_filters__ = [
        ("set_player", (Command("set_player"),)),
        ("lang", (Command("lang"),)),
        ("set_nick", (F.text.regexp(RawRegex.nickname), SetPlayerStates.set_nick)),
        ("invalid_nickname", (SetPlayerStates.set_nick,))
        ]

    def init(self) -> None:
        self.api = API()
        self.pdb = PlayersDB()
    
    async def _save_player(self, msg: 'Message', region: str, nickname: str, slot: str, bot: 'Bot', player: 'GameAccount | None' = None) -> None:
        if not player:
            player = await self.api.check_and_get_player(
                    region,
                    nickname
                )
        slot = AccountSlotsEnum[slot]

        await self.pdb.set_member(slot, msg.from_user.id, player, slot_override=True)

        await bot.send_message(msg.chat.id, 
                                    Text().get().cmds.set_player.info.set_player_ok)
        _log.info(f"Set player: {player.nickname} for {msg.from_user.id}")
    
    @HookExceptions().hook(_log)
    @Activities.typing
    async def invalid_nickname(self, msg: 'Message', bot: 'Bot', **_):
        await bot.send_message(msg.chat.id, Text().get().cmds.set_player.info.invalid_nickname)
    
    @HookExceptions().hook(_log)
    @Activities.typing
    async def set_nick(self, msg: 'Message', state: 'FSMContext', bot: 'Bot', **_):
        region = (await state.get_data())["data"]["region"]
        nickname = msg.text

        try:
            player = await self.api.check_and_get_player(
                region,
                nickname
            )
        except:
            await msg.reply(Text().get().cmds.set_player.info.invalid_nickname)
            return
        else:
            await state.update_data(data={"data": None})
            await state.set_state()

        if await self.pdb.check_member_exists(msg.from_user.id, raise_error=False):
            await state.update_data(data={"data": player})
            member = await self.pdb.get_member(msg.from_user.id)
            await bot.send_message(msg.chat.id, Text().get().cmds.set_player.info.choose_slot, 
                                    reply_markup=Buttons.sp_choose_slot(member.game_accounts.as_dict(), 
                                                                        await self.pdb.check_premium(member=member)).get_keyboard(1))
            return
        else:
            slot = "slot_1"
        
        await self._save_player(msg, region, nickname, slot, bot, player)
    
    @HookExceptions().hook(_log)
    @Activities.typing
    @check(in_db=False)
    @analytics("set_player")
    @parse_message(max_args=3, min_args=2, raise_error=False)
    async def set_player(self, msg: 'Message', splitted_message: list[str], state: 'FSMContext', bot: 'Bot', **_):
        try:
            n_type = validate(splitted_message[0], 'nickname')
            compisite_nickname = handle_nickname(splitted_message[0], n_type)
            region = splitted_message[1]
            try:
                slot = f'slot_{int(splitted_message[2])}'
            except KeyError:
                slot = f'slot_1'
            
            await self._save_player(msg, region, compisite_nickname.nickname, slot, bot)
        except IndexError:
            if not (msg.chat.type == "private"):
                await bot.send_message(msg.chat.id, Text().get().frequent.errors.missing_argument)
                return
            await msg.reply(Text().get().cmds.set_player.sub_descr.get_region, 
                            reply_markup=Buttons.set_player_buttons().get_keyboard(4))
            
    @HookExceptions().hook(_log)
    @Activities.typing
    @check()
    async def lang(self, msg: 'Message', bot: 'Bot', **_):
        await bot.send_message(msg.chat.id, Text().get().cmds.set_lang.sub_descr.choose_lang,
                                    reply_markup=Buttons.set_lang_buttons().get_keyboard(4))
