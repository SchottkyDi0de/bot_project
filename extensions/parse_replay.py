from uuid import uuid4
from typing import TYPE_CHECKING

from aiogram.filters import Command
from aiogram.types import ReactionTypeEmoji

from extensions.setup import ExtensionsSetup
from lib import (Activities, Buttons, HookExceptions, ReplayStates, ReplayParser, 
                 Text, analytics, check)

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message
    from aiogram.fsm.context import FSMContext

class Replay(ExtensionsSetup):
    __funcs_filters__ = [
        ("replay", (Command("replay"),)),
        ("file_replay", (ReplayStates.gf,))
    ]

    @HookExceptions().hook()
    @Activities.typing
    @check()
    @analytics("replay")
    async def replay(self, msg: 'Message', state: 'FSMContext', **_):
        await state.set_state(ReplayStates.gf)
        smsg = await msg.reply(Text().get().cmds.parse_replay.info.send_file,
                               reply_markup=Buttons.parse_replay_main_back_buttons().get_keyboard())

        await state.update_data(data={"data": smsg})
    
    @HookExceptions().hook()
    async def file_replay(self, msg: 'Message', state: 'FSMContext', bot: 'Bot', **_):
        if msg.document is None or msg.document.file_size > 1.1e7:      #1.1e7 = ~10.5MB
            await bot.set_message_reaction(msg.chat.id, msg.message_id, [ReactionTypeEmoji(emoji="👎")])
            return
        path = f"tmp/{uuid4()}"

        with open(path, 'wb') as f:
            await bot.download(msg.document.file_id, f)
        
        await (await state.get_data())["data"].delete()
        
        replay_data = ReplayParser().parse(path)
        await state.set_state()
        await state.update_data(data={"data": replay_data})
        await msg.reply(text=Text().get().cmds.parse_replay.info.choose_region,
                        reply_markup=Buttons.pr_region_buttons().get_keyboard(4))
