class ReplayParserError(BaseException):
    pass

class PathNotExists(ReplayParserError):
    pass

class WrongFileType(ReplayParserError):
    pass