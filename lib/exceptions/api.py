class APIError(Exception):
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
