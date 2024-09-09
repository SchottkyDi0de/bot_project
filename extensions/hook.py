from typing import TYPE_CHECKING

from aiogram import F
from aiogram.types import ReactionTypeEmoji
from aiogram.filters import Command

from lib.utils.validators import RawRegex

from extensions.setup import ExtensionsSetup
from lib import API, Activities, Text, Buttons, HookExceptions, HookStates, PlayersDB, analytics, check
from lib.buttons.functions import Functions

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message
    from aiogram.fsm.context import FSMContext
    
    from lib.data_classes.db_player import HookStats


class Hook(ExtensionsSetup):
    __funcs_filters__ = [
        ("hook", (Command("hook"),)),
        ("target_nickname", (F.text.regexp(RawRegex.nickname), HookStates.target_nickname)),
        ("invalid_nickname", (HookStates.target_nickname,)),
        ("target_value", (HookStates.target_value,)),
    ]

    def init(self):
        self.pdb = PlayersDB()
        self.api = API()

    @HookExceptions().hook()
    @Activities.typing
    @check()
    @analytics()
    async def hook(self, msg: 'Message', state: 'FSMContext', **_):
        member = await self.pdb.get_member(msg.from_user.id)

        if member.hook_stats.active:
            await msg.reply(Text().get().cmds.hook.info.active_descr, 
                            reply_markup=Buttons.hook_buttons().get_keyboard(1))
            return
        
        await Functions.new_hook(msg, state, member)

    @HookExceptions().hook()
    @Activities.typing
    async def target_nickname(self, msg: 'Message', state: 'FSMContext', **_):
        state_data: 'HookStats' = (await state.get_data())["data"]

        nickname = msg.text
        stats = await self.api.get_stats(state_data.target_region, search=nickname, ignore_lock=True)
        if isinstance(stats, str):
            await msg.reply(stats + "\n" + Text().get().frequent.info.try_again)
            return

        state_data.target_nickname = nickname
        state_data.last_stats = stats
        await state.set_state()

        keyboard = Buttons.hook_target_stats_buttons().format_data(3)
        keyboard += Buttons.hook_rating_onoff_buttons(False).format_data(1)

        await msg.reply(Text().get().cmds.hook.info.choose_target_stats,
                        reply_markup=keyboard.get_keyboard())

    @HookExceptions().hook()
    async def invalid_nickname(self, msg: 'Message', bot: 'Bot', **_):
        await bot.set_message_reaction(msg.chat.id, msg.message_id, [ReactionTypeEmoji(emoji="👎")])

    @HookExceptions().hook()
    async def target_value(self, msg: 'Message', state: 'FSMContext', bot: 'Bot', **_):
        state_data: 'HookStats' = (await state.get_data())["data"]

        try:
            value = int(msg.text.strip())
        except TypeError:
            await bot.set_message_reaction(msg.chat.id, msg.message_id, [ReactionTypeEmoji(emoji="👎")])
            return
        else:
            state_data.target_value = value
        
        state_data.active = True
        
        await state.set_state()
        await msg.reply(Text().get().cmds.hook.sub_descr.watch_for,
                        reply_markup=Buttons.hook_watch_for_buttons().get_keyboard(1))
