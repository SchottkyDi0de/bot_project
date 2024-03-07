from lib.utils.validators import CompiledRegex, NickTypes


class CompositeNickname:
    nickname: str = None
    player_id: int = None
    

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