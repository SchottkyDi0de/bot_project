from discord.ext.commands import CommandError


class APIError(CommandError, Exception):
    pass

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