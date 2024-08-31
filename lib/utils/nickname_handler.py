from lib.utils.validators import CompiledRegex, NickTypes


class CompositeNickname:
    nickname: str = None
    player_id: int = None
    region: str = None
    

def handle_nickname(nickname: str, type: NickTypes) -> CompositeNickname:
    data = CompositeNickname()
    if type is NickTypes.COMPLETION:
        nickname_data = nickname.split(' | ')
        data.player_id = int(nickname_data[0])
        data.nickname = nickname_data[1]
        data.region = nickname_data[2].lower()
        return data
        
    if type is NickTypes.PLAYER_ID:
        data.player_id = int(nickname)
        return data
    
    elif type is NickTypes.NICKNAME_AND_ID:
        nickname = CompiledRegex.delete_sym.sub('', nickname)
        data.nickname = nickname.split('/')[0]
        data.player_id = int(nickname.split('/')[1])
        return data
    
    elif type is NickTypes.NICKNAME:
        nickname = CompiledRegex.delete_sym.sub('', nickname)
        data.nickname = nickname
        return data
