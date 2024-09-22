from typing import TYPE_CHECKING

from aiogram.filters import Command

from lib.utils.string_parser import insert_data

from extensions.setup import ExtensionsSetup
from lib import Buttons, Config, PlayersDB, Text, HookExceptions, Activities, analytics, check

if TYPE_CHECKING:
    from aiogram.types import Message

_config = Config().config


class SessionWidget(ExtensionsSetup):
    __funcs_filters__ = [
        ("session_widget", (Command("session_widget"),))
    ]

    def init(self):
        self.pdb = PlayersDB()

    @HookExceptions().hook()
    @Activities.typing
    @check()
    @analytics()
    async def session_widget(self, msg: 'Message', **_):
        author_id = msg.from_user.id
        player = await self.pdb.get_member(author_id)
        url = insert_data(_config.session_widget.url,
                           {
                               "user_id": author_id,
                               "lang": player.lang if player.lang else "en"
                            })
        
        await msg.reply(insert_data(Text().get().cmds.session_widget.info.success,
                                    {"link": url}), 
                        reply_markup=Buttons.session_widget_buttons(url).get_keyboard(),
                        parse_mode="MarkdownV2")
