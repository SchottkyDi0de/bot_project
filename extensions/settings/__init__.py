from typing import TYPE_CHECKING

from aiogram.filters import Command

from lib.logger.logger import get_logger

from extensions.setup import ExtensionsSetup
from lib import Buttons, Text, HookExceptions, Activities, analytics, check, init_files

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message

init_files("extensions.settings", ['__init__.py'])
_log = get_logger(__file__, 'TgSettingsLogger', 'logs/tg_settings.log')


class Settings(ExtensionsSetup):
    __funcs_filters__ = [
        ("settings", (Command("settings"),)),
    ]

    @HookExceptions().hook(_log)
    @Activities.typing
    @check()
    @analytics()
    async def settings(self, msg: 'Message', bot: 'Bot', **_):
        await bot.send_message(msg.chat.id, Text().get().cmds.settings.sub_descr.main_text,
                                    reply_markup=Buttons.settings_buttons().get_keyboard(1))
