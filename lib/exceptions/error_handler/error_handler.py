import traceback
from typing import Coroutine

from discord.commands import ApplicationContext
from discord.ext import commands
from logging import Logger

from lib.embeds.info import InfoMSG
from lib.embeds.errors import ErrorMSG

from lib.exceptions import api, data_parser, database, replay_parser
from lib.exceptions.blacklist import UserBanned
from lib.exceptions.nickname_validator import NicknameValidationError


def error_handler(_log: Logger) -> Coroutine:

    async def inner(_, ctx: ApplicationContext, error: commands.CommandError):
        inf_msg = InfoMSG()
        err_msg = ErrorMSG()
        kwargs = {}
        

        if isinstance(error, commands.CommandOnCooldown):
            embed = inf_msg.cooldown_not_expired()
            kwargs |= {"ephemeral": True}
        elif isinstance(error, UserBanned):
            embed = err_msg.user_banned()
        elif isinstance(error, NicknameValidationError):
            embed = err_msg.uncorrect_name()
        elif isinstance(error, api.APIError):
            if isinstance(error, api.NoPlayersFound):
                embed = err_msg.player_not_found()
            elif isinstance(error, api.UncorrectName):
                embed = err_msg.uncorrect_name()
            elif isinstance(error, api.NeedMoreBattlesError):
                embed = err_msg.need_more_battles()
            else:
                _log.error(traceback.format_exc())
                embed = err_msg.api_error()
        elif isinstance(error, database.DatabaseError):
            if isinstance(error, database.LastStatsNotFound):
                embed = err_msg.session_not_found()
        elif isinstance(error, data_parser.DataParserError):
            if isinstance(error, data_parser.NoDiffData):
                embed = err_msg.session_not_updated()
            else:
                embed = err_msg.parser_error()
        elif isinstance(error, replay_parser.ReplayParserError):
            if isinstance(error, replay_parser.WrongFileType):
                embed = err_msg.wrong_file_type()
        else:
            _log.error(traceback.format_exc())
            embed = err_msg.unknown_error()
        
        await ctx.respond(embed=embed, **kwargs)

    return inner