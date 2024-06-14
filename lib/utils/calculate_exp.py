from random import randint

def exp_calc(command_name: str) -> int:
    if command_name == 'report':
        return randint(10, 80)
    elif command_name in ['profile', 'set_lang', 'switch_account']:
        return 1
    elif command_name == 'help':
        return 2
    elif command_name in ['stats', 'astats']:
        return randint(5, 20)
    elif command_name == 'get_session':
        return randint(10, 25)
    elif command_name == 'start_session':
        return randint(5, 15)
    elif command_name == "parse_replay":
        return randint(2, 40)
    elif command_name == 'set_background':
        return randint(10, 35)
    elif command_name == 'set_player':
        return 20
    elif command_name == 'verify':
        return 5
    elif command_name == 'set_lock':
        return randint(5, 10)
    else:
        return randint(1, 15)
