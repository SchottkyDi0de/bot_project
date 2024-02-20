from re import compile as _compile
from enum import Enum

from lib.exceptions.nickname_validator import NicknameValidationError


class CompiledRegex:
    nickname_and_id = _compile(r'[("]?([A-Za-z0-9_]{3,24})[)"]?/([0-9]+)')
    nickname = _compile(r'[("]?([A-Za-z0-9_]{3,24})[)"]?')
    player_id = _compile(r'([0-9]+)')
    delete_sym = _compile(r'["()]')


class NickTypes(Enum):
    NICKNAME = 0
    PLAYER_ID = 1
    NICKNAME_AND_ID = 2


class CompositeNickname:
    nickname: str = None
    player_id: int = None


def validate_nickname(nickname: str):
    nickname_len = len(nickname)
    player_id = CompiledRegex.player_id.match(nickname)
    nickname_and_id = CompiledRegex.nickname_and_id.match(nickname)
    nick = CompiledRegex.nickname.match(nickname)

    if player_id and player_id.span()[1] == nickname_len:
        return NickTypes.PLAYER_ID
    if nickname_and_id and nickname_and_id.span()[1] == nickname_len:
        return NickTypes.NICKNAME_AND_ID
    if nick and nick.span()[1] == nickname_len:
        return NickTypes.NICKNAME
    raise NicknameValidationError
    

def handle_nickname(nickname: str, type: NickTypes) -> CompositeNickname:
    data = CompositeNickname()
    if type == NickTypes.PLAYER_ID:
        data.player_id = int(nickname)
        return data
    elif type == NickTypes.NICKNAME_AND_ID:
        nickname = CompiledRegex.delete_sym.sub('', nickname)
        data.nickname = nickname.split('/')[0]
        data.player_id = int(nickname.split('/')[1])
        return data
    elif type == NickTypes.NICKNAME:
        nickname = CompiledRegex.delete_sym.sub('', nickname)
        data.nickname = nickname
        return data