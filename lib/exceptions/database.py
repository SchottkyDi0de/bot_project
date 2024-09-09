class DatabaseError(Exception):
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

class PremiumSlotAccessAttempt(DatabaseError):
    pass

class PremiumNotFound(DatabaseError):
    pass

class SlotIsNotEmpty(DatabaseError):
    pass

class SlotIsEmpty(DatabaseError):
    pass

class InvalidSlot(DatabaseError):
    pass
