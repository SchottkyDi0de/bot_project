from typing import TYPE_CHECKING, Coroutine, Callable

from lib.exceptions import parse

if TYPE_CHECKING:
    from aiogram.types import Message


def parse_message(max_args: int, min_args: int=0, *, include_first_arg: bool=False, raise_error: bool=True) -> Callable:
    def inner(func: Callable) -> Coroutine:
        async def wrapper(self, data: 'Message', *args, **kwargs):
            splitted_message = data.text.split()
            if raise_error:
                if min_args <= len(splitted_message if include_first_arg else splitted_message[1:]) <= max_args:
                    return await func(self, data, splitted_message if include_first_arg else splitted_message[1:], *args, **kwargs)
                else:
                    if len(splitted_message[1:]) < min_args:
                        raise parse.MissingArgumentsError
                    else:
                        raise parse.TooManyArgumentsError
            else:
                return await func(self, data, splitted_message if include_first_arg else splitted_message[1:], *args, **kwargs)
                    
        return wrapper
    return inner
    