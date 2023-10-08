class DatabaseError(BaseException):
    pass

class MemberNotFound(DatabaseError):
    pass

class LastStatsNotFound(DatabaseError):
    pass

class TankNotFoundInTankopedia(DatabaseError):
    pass

class ServerNotFound(DatabaseError):
    pass