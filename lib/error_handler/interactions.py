from functools import wraps
from collections.abc import Awaitable
import logging
from logging import Logger
import traceback

from discord.ext import commands
from discord import Interaction

from lib.embeds.errors import ErrorMSG
from lib.embeds.info import InfoMSG
from lib.exceptions import api, data_parser
from lib.exceptions.blacklist import UserBanned, BlackListException


def hook_exceptions(interaction: Interaction, logger: Logger) -> Awaitable:
    """
    Decorator function that catches exceptions raised by an interaction callback and logs them.
    
    Args:
        interaction (Interaction): The interaction object.
        logger (Logger): The logger object.
    
    Returns:
        A decorator function that wraps the original interaction callback and handles exceptions.
    
    Raises:
        None
    
    Example:
        @hook_exceptions(interaction, logger)
        async def my_callback():
            # Original interaction callback code
    
    """
    def decorator(wrapped_func) -> Awaitable:
        def log_error(exception: Exception, short: bool = False, log_level: int = logging.ERROR) -> None:
            logger.log(
                level=log_level, 
                msg=f'Exception on wrapped interaction callback: {wrapped_func.__name__} | {exception.__class__.__name__}'
            )
            exc_message = ''
            if short:
                if hasattr(exception, 'message'):
                    exc_message = exception.message
                else:
                    exc_message = str(exception)
            else:
                exc_message = traceback.format_exc()
            logger.log(level=log_level, msg=f'{exception.__class__.__name__} | {exc_message}')
            
        @wraps(wrapped_func)
        async def wrapper(*args, **kwargs) -> Awaitable:
            try:
                await wrapped_func(*args, **kwargs)
            except commands.CommandError as exception:
                if isinstance(exception, commands.CommandOnCooldown):
                    await interaction.response.send_message(
                        embed=InfoMSG().cooldown_not_expired(), ephemeral=True
                    )
                    log_error(exception, short=True, log_level=logging.DEBUG)
                    return
                
                if isinstance(exception, BlackListException):
                    if isinstance(exception, UserBanned):
                        await interaction.response.send_message(
                            embed=ErrorMSG().user_banned(), ephemeral=True
                        )
                        log_error(exception, short=True, log_level=logging.INFO)
                        return
                    else:
                        await interaction.response.send_message(
                            embed=ErrorMSG().unknown_error(), ephemeral=True
                        )
                        log_error(exception)
                        return
                    
                elif isinstance(exception, api.APIError):
                    if isinstance(exception, api.NoPlayersFound):
                        await interaction.response.send_message(
                            embed=ErrorMSG().player_not_found(), ephemeral=True
                        )
                        log_error(exception, short=True, log_level=logging.DEBUG)
                        return
                    else:
                        await interaction.response.send_message(
                            embed=ErrorMSG().api_error(real_exc=exception.real_exc), ephemeral=True
                        )
                        log_error(exception)
                        return
                    
                elif isinstance(exception, data_parser.DataParserError):
                    if isinstance(exception, data_parser.NoDiffData):
                        await interaction.response.send_message(
                            embed=ErrorMSG().session_not_updated(), ephemeral=True
                        )
                        log_error(exception)
                        return
                    else:
                        await interaction.response.send_message(
                            embed=ErrorMSG().unknown_error(), ephemeral=True
                        )
                        log_error(exception)
                        return
                    
        return wrapper
    return decorator
