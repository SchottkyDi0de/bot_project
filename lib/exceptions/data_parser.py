from discord.ext.commands import CommandError


class DataParserError(CommandError, Exception):
    pass

class NoDiffData(DataParserError):
    pass