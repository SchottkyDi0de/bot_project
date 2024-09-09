class BlackListException(BaseException):
    pass


class UserBanned(BlackListException):
    pass