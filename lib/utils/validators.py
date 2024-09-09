from re import compile as _compile
from enum import Enum
from typing import Any, Literal

from lib.exceptions.nickname_validator import NicknameValidationError


class RawRegex:
    nickname_and_id = r'^[("]?([A-Za-z0-9_]{3,24})[)"]?/([0-9]+)$'
    nickname = r'^[("]?([A-Za-z0-9_]{3,24})[)"]?$'
    player_id = r'^([0-9]+)$'
    delete_sym = r'["()]'
    time = r'\b([01][0-9]|2[0-3]):([0-5][0-9])\b'


class CompiledRegex:
    nickname_and_id = _compile(RawRegex.nickname_and_id)
    nickname = _compile(RawRegex.nickname)
    player_id = _compile(RawRegex.player_id)
    delete_sym = _compile(RawRegex.delete_sym)
    time = _compile(RawRegex.time)



class NickTypes(Enum):
    NICKNAME = 0
    PLAYER_ID = 1
    NICKNAME_AND_ID = 2


class Validatos:
    def get_validator(type: Literal["nickname", "time"]):
        return getattr(Validatos, f"validate_{type}")
    def validate_time(time_str: str | None) -> bool:
        if time_str is None:
            return False
    
        return CompiledRegex.time.match(time_str) is not None

    def validate_nickname(nickname: str):
        if ' | ' in nickname:
            nickname = nickname.split(' | ')[0].strip()
        
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


def validate(data: Any, type: Literal["nickname", "time"]):
    validator = Validatos.get_validator(type)
    return validator(data)
