from collections.abc import Callable
from functools import wraps

from aiohttp import ServerTimeoutError

from lib.exceptions.api import APIError
from lib.settings.settings import Config

_config = Config().get()

def timeout_handler(reg_param_name: str = 'region') -> Callable:
    """Async decorator for providing additional data for CliientTimeOut exception"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ServerTimeoutError:
                err_msg = (
                    f"APIError: ServerTimeoutError\n"
                    f"⤷ Method '{func.__name__}' timed out.\n"
                )


                if reg_param_name in kwargs.keys():
                    reg = kwargs[reg_param_name]
                    match reg:
                        case 'ru':
                            url = _config.game_api.reg_urls.ru
                        case 'eu':
                            url = _config.game_api.reg_urls.eu
                        case 'asia':
                            url = _config.game_api.reg_urls.asia
                        case 'com' | 'na':
                            url = _config.game_api.reg_urls.na
                    err_msg = err_msg + f"  ⤷ API URL '{url}' did not respond!"
                    
                raise APIError(real_exc=TimeoutError(err_msg))

        return wrapper
    
    return decorator
