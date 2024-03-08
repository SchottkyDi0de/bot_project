from discord.ext.commands import CommandError


class NicknameValidationError(CommandError, Exception):
    pass
