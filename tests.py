from string import ascii_letters, digits
from random import choice, randint

from lib.utils.nickname_handler import NickTypes, validate_nickname

sym = [*(ascii_letters + digits + '_')]


def gen_data():
    type = choice((NickTypes.NICKNAME,))
    match type:
        case NickTypes.NICKNAME:
            return ''.join(choice(sym) for _ in range(randint(3, 24))), type
        case NickTypes.PLAYER_ID:
            return str(randint(1000, 100000)), type
        case NickTypes.NICKNAME_AND_ID:
            return f'{"".join(choice(sym) for _ in range(randint(3, 24)))}/{str(randint(1000, 100000))}', type


for i in range(1, 101):
    data = gen_data()
    print(f'{data=}')
    res = validate_nickname(data[0])
    print(f'{res=}')
    assert res == data[1]
    print(f"test {i} complete")
