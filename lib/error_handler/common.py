import traceback
from logging import Logger
from typing import Coroutine

from discord.commands import ApplicationContext
from discord.ext import commands

from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.exceptions import api, data_parser, database, replay_parser
from lib.exceptions.blacklist import UserBanned
from lib.exceptions.nickname_validator import NicknameValidationError

from lib.locale.locale import Text


def hook_exceptions(_log: Logger) -> Coroutine:

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
            elif isinstance(error, api.LockedPlayer):
                embed = err_msg.locked_player()
            else:
                _log.error(traceback.format_exc())
                embed = err_msg.api_error()
        elif isinstance(error, database.DatabaseError):
            if isinstance(error, database.LastStatsNotFound):
                embed = inf_msg.custom(
                    locale=Text().get(),
                    text=Text().get().cmds.get_session.errors.session_not_found,
                    colour='orange'
                )
            elif isinstance(error, database.VerificationNotFound):
                embed = inf_msg.member_not_verified()
            elif isinstance(error, database.SlotIsEmpty):
                embed = inf_msg.custom(
                    locale=Text().get(),
                    title=Text().get().frequent.info.warning,
                    text=Text().get().frequent.errors.slot_is_empty,
                    colour='orange'
                )
            elif isinstance(error, database.PremiumSlotAccessAttempt):
                embed = inf_msg.custom(
                    locale=Text().get(),
                    colour='orange',
                    text=Text().get().frequent.errors.slot_not_accessed,
                )
            elif isinstance(error, database.MemberNotFound):
                embed = inf_msg.player_not_registered()
            elif isinstance(error, database.PremiumNotFound):
                embed = inf_msg.custom(
                    locale=Text().get(),
                    text=Text().get().frequent.errors.premium_not_found,
                    colour='orange',
                )
            else:
                embed = err_msg.unknown_error()
        elif isinstance(error, data_parser.DataParserError):
            if isinstance(error, data_parser.NoDiffData):
                embed = inf_msg.custom(
                    locale=Text().get(),
                    text=Text().get().cmds.get_session.errors.session_not_updated,
                    colour='orange'
                )
            else:
                embed = err_msg.parser_error()
        elif isinstance(error, replay_parser.ReplayParserError):
            if isinstance(error, replay_parser.WrongFileType):
                embed = err_msg.wrong_file_type()
            else:
                _log.error(traceback.format_exc())
                embed = err_msg.unknown_error()
        else:
            _log.error(traceback.format_exc())
            embed = err_msg.unknown_error()
        
        await ctx.respond(embed=embed, **kwargs)

    return inner
