from discord.ext.commands import CommandError


class ReplayParserError(CommandError, BaseException):
    pass

class PathNotExists(ReplayParserError):
    pass

class WrongFileType(ReplayParserError):
    pass