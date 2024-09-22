from ast import literal_eval
from typing import TYPE_CHECKING

from aiogram.types import BufferedInputFile
from aiogram.filters import Command

from pydantic import BaseModel

from extensions.setup import ExtensionsSetup
from lib import Buttons, PlayersDB, HookExceptions, SetPlayerStates, Text, analytics, check

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message
    from aiogram.fsm.context import FSMContext


class Common(ExtensionsSetup):
    __funcs_filters__ = [
        ("start", (Command("start"),)),
        ("help", (Command("help"),)),
        ("db", (Command("db"),)),
        ]
    
    def init(self):
        self.pdb = PlayersDB()

    @HookExceptions().hook()
    @analytics()
    async def start(self, msg: 'Message', bot: 'Bot', state: 'FSMContext', **_):
        await bot.send_message(msg.chat.id, Text().get().cmds.start.descr)
        if msg.chat.type == "private" and not await self.pdb.get_member(msg.from_user.id, False):
            await bot.send_message(msg.chat.id, Text().get().cmds.set_player.sub_descr.get_region,
                                   reply_markup=Buttons.set_player_buttons().get_keyboard(4))
    
    @HookExceptions().hook()
    @analytics()
    async def help(self, msg: 'Message', bot: 'Bot', **_):
        await msg.reply(Text().get().cmds.help.descr, 
                        reply_markup=Buttons.help_buttons(await bot.get_me()).get_keyboard(1))

    @check(developer_only=True)
    async def db(self, msg: 'Message', bot: 'Bot', **_):
        try:
            params = msg.text.replace("!me", f"{msg.from_user.id}").strip().split()[1:]

            if params[0] not in ["get", "set"]:
                return
        
            mode = params[0]
            user_id = params[1]
            path = []
            doted_path = ""
            if params[2:]:
                path = params[2].split(".")
                doted_path = params[2]
            if mode == "get":
                player = await self.pdb.get_member(user_id)
                temp = player
                for name in path:
                    temp = getattr(temp, name)
                if isinstance(temp, BaseModel):
                    model_text = temp.model_dump_json(indent=2)
                    if len(model_text) < 2000:
                        await msg.reply(f"```JSON\n{model_text}```", parse_mode="MarkdownV2")
                    else:
                        await bot.send_document(msg.chat.id, 
                                                BufferedInputFile(model_text.encode("utf-8"), "model.txt"),
                                                caption="succes")
                else:
                    await msg.reply(f"{temp}")
            else:
                if params[3:]:
                    value = literal_eval(" ".join(params[3:]))
                else:
                    return
                await self.pdb.set_one(user_id, doted_path, value)
                await msg.reply("succes")

        except Exception:
            return

