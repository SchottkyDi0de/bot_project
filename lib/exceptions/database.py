from discord.ext.commands import CommandError


class DatabaseError(CommandError, Exception):
    pass

class MemberNotFound(DatabaseError):
    pass

class LastStatsNotFound(DatabaseError):
    pass

class TankNotFoundInTankopedia(DatabaseError):
    pass

class ServerNotFound(DatabaseError):
    pass

class MemberNotVerified(DatabaseError):
    pass

class OperationAccessDenied(DatabaseError):
    pass

class AutosessionNotFound(DatabaseError):
    pass