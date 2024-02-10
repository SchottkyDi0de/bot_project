from discord.ext.commands import CommandError


class BlackListException(CommandError, BaseException):
    pass


class UserBanned(BlackListException):
    pass