from typing import Any
from discord.ext.commands import CommandError


class APIError(CommandError, Exception):
    '''
    Base Class for custom API exceptions
    '''
    def __init__(self, message: str | None = None, real_exc: Exception | None = None, *args: Any) -> None:
        super().__init__(message, *args)
        self.real_exc = real_exc

class UncorrectName(APIError):
    pass

class MoreThanOnePlayerFound(APIError):
    pass

class NoPlayersFound(APIError):
    pass

class EmptyDataError(APIError):
    pass

class NeedMoreBattlesError(APIError):
    pass

class UncorrectRegion(APIError):
    pass

class RequestsLimitExceeded(APIError):
    pass

class APISourceNotAvailable(APIError):
    pass

class LockedPlayer(APIError):
    pass