class BlackListException(Exception):
    pass

class UserBanned(BlackListException):
    pass