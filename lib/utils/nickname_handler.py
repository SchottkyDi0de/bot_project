from enum import Enum

from lib.exceptions.nickname_validator import NicknameInvalidLength, NicknameValidationError


class NickTypes(Enum):
    NICKNAME = 0
    PLAYER_ID = 1
    NICKNAME_AND_ID = 2


class CompositeNickname:
    nickname: str = None
    player_id: int = None


def validate_nickname(nickname: str):
    try:
        int(nickname)
    except ValueError:
        pass
    else:
        return NickTypes.PLAYER_ID

    nick_and_id = nickname.split('/')
    
    try:
        int(nick_and_id[1])
    except ValueError:
        raise NicknameValidationError()
    except IndexError:
        if len(nick_and_id[0]) < 3 or len(nick_and_id[0]) > 24:
            raise NicknameInvalidLength()
        
        return NickTypes.NICKNAME
    else:
        return NickTypes.NICKNAME_AND_ID
    

def handle_nickname(nickname: str, type: NickTypes) -> CompositeNickname:
    data = CompositeNickname()
    if type == NickTypes.PLAYER_ID:
        data.player_id = int(nickname)
        return data
    elif type == NickTypes.NICKNAME_AND_ID:
        nickname = nickname.replace('"', '')
        nickname = nickname.replace(')', '')
        nickname = nickname.replace('(', '')
        data.nickname = nickname.split('/')[0]
        data.player_id = int(nickname.split('/')[1])
        return data
    elif type == NickTypes.NICKNAME:
        nickname = nickname.replace('"', '')
        nickname = nickname.replace(')', '')
        nickname = nickname.replace('(', '')
        data.nickname = nickname
        return data