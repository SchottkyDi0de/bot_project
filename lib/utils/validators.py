from re import compile as _compile
from enum import Enum
from typing import Any, Literal

from lib.exceptions.nickname_validator import NicknameValidationError


class CompiledRegex:
    nickname_and_id = _compile(r'[("]?([A-Za-z0-9_]{3,24})[)"]?/([0-9]+)')
    nickname = _compile(r'[("]?([A-Za-z0-9_]{3,24})[)"]?')
    player_id = _compile(r'([0-9]+)')
    delete_sym = _compile(r'["()]')
    time = _compile(r'\b([01][0-9]|2[0-3]):([0-5][0-9])\b')


class NickTypes(Enum):
    NICKNAME = 0
    PLAYER_ID = 1
    NICKNAME_AND_ID = 2
    COMPLETION = 3


class Validators:
    def get_validator(type: Literal["nickname", "time"]):
        return getattr(Validators, f"validate_{type}")
    def validate_time(time_str: str | None) -> bool:
        if time_str is None:
            return False
    
        return CompiledRegex.time.match(time_str) is not None

    def validate_nickname(nickname: str):
        if ' | ' in nickname:
            return NickTypes.COMPLETION
        
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


def validate(data: Any, type: Literal["nickname", "time"]) -> NickTypes:
    validator = Validators.get_validator(type)
    return validator(data)
