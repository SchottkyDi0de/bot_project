import traceback
from logging import Logger
from typing import Callable

from aiogram import Bot
from aiogram.types import Message, CallbackQuery

from lib.database.players import PlayersDB
from lib.exceptions import api, data_parser, database, replay_parser
from lib.exceptions.blacklist import UserBanned
from lib.exceptions.nickname_validator import NicknameValidationError
from lib.logger.logger import get_logger
from lib.utils.singleton_factory import singleton
from lib.utils.string_parser import insert_data

from lib.locale.locale import Text
from lib.exceptions import parse
from lib.exceptions.cooldown import CooldownError
from workers import AutoDeleteMessage

err_logger = get_logger(__file__, 'TgErrorHandler', 'logs/tg_error.log')

@singleton
class HookExceptions:
    """catches exceptions, auto loads localization for user"""
    pdb = PlayersDB()

    def hook(hself, _log: Logger=err_logger, del_message_on_error: bool = False) -> Callable:
        def inner1(func: Callable) -> Callable:
            async def inner2(fself, data: Message | CallbackQuery, bot: Bot, *args, **kwargs):
                await Text().load_by_data(data, await hself.pdb.get_member(data.from_user.id, raise_error=False))

                try:
                    return await func(fself, data, bot=bot, *args, **kwargs)
                except Exception as error:
                    if isinstance(data, CallbackQuery):
                        data = data.message
                    if del_message_on_error:
                        await data.delete()
                        err_logger.info(f"Delete message {data.message_id} in {data.chat.id} on error:\n" 
                                          f"{error}")
                    else:
                        AutoDeleteMessage.add2list(await bot.send_message(data.chat.id, hself._get_text(_log, error)), 
                                                   15)

            return inner2
        return inner1

    def _get_text(self, _log: Logger, error: Exception) -> str:
        text = ''
        locale = Text().get()

        if isinstance(error, UserBanned):
            text = locale.frequent.errors.user_banned
        elif isinstance(error, CooldownError):
            text = insert_data(locale.frequent.errors.cooldown,
                               {"time": error.wait})
        elif isinstance(error, NicknameValidationError):
            text = locale.cmds.stats.errors.uncorrect_nickname
        elif isinstance(error, api.APIError):
            if isinstance(error, api.NoPlayersFound):
                text = locale.cmds.stats.errors.player_not_found
            elif isinstance(error, api.UncorrectName):
                text = locale.cmds.stats.errors.uncorrect_nickname
            elif isinstance(error, api.NeedMoreBattlesError):
                text = locale.cmds.stats.errors.no_battles
            else:
                _log.error(traceback.format_exc())
                text = locale.frequent.errors.api_error
        elif isinstance(error, database.DatabaseError):
            if isinstance(error, database.LastStatsNotFound):
                text = locale.cmds.session_state.errors.session_not_found
        elif isinstance(error, data_parser.DataParserError):
            if isinstance(error, data_parser.NoDiffData):
                text = locale.cmds.get_session.errors.session_not_found
            else:
                text = locale.cmds.parse_replay.errors.parsing_error
        elif isinstance(error, replay_parser.ReplayParserError):
            if isinstance(error, replay_parser.WrongFileType):
                text = locale.frequent.errors.wrong_file_type
            else:
                _log.error(traceback.format_exc())
                text = locale.frequent.errors.unknown_error
        elif isinstance(error, parse.BaseParseError):
            if isinstance(error, parse.MissingArgumentsError):
                text = locale.frequent.errors.missing_argument
            elif isinstance(error, parse.TooManyArgumentsError):
                text = locale.frequent.errors.too_many_arguments
            elif isinstance(error, parse.InvalidArgumentError):
                text = locale.frequent.errors.invalid_argument
        else:
            _log.error(traceback.format_exc())
            text = locale.frequent.errors.unknown_error
    
        return text
