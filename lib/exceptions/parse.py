class BaseParseError(Exception):
    ...


class MissingArgumentsError(BaseParseError):
    ...


class TooManyArgumentsError(BaseParseError):
    ...


class InvalidArgumentError(BaseParseError):
    ...
