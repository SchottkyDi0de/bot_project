from random import randint

INITIAL_LEVEL_EXP = 40


class LevelInfo:
    def __init__(self, level: int, rem_exp: int, next_exp: int):
        self.level = level
        self.rem_exp = rem_exp
        self.next_exp = next_exp

def exp_add(command_name: str) -> int:
    """
    Calculates the experience points to be added based on the given command name.

    Args:
        command_name (str): The name of the command.

    Returns:
        int: The experience points to be added.

    """
    if command_name == 'report':
        return randint(10, 80)
    elif command_name in ['profile', 'lang']:
        return 1
    elif command_name == 'help':
        return 2
    elif command_name == 'stats':
        return randint(5, 20)
    elif command_name == 'get_session':
        return randint(10, 25)
    elif command_name == 'start_session':
        return randint(5, 15)
    elif command_name == "replay":
        return randint(2, 40)
    elif command_name == 'set_player':
        return 20
    else:
        return randint(1, 15)
    
def get_level(exp: int) -> LevelInfo:
    """
    Calculate the level based on the experience points provided.
    
    Parameters:
    exp (int): The experience points to calculate the level from.
    
    Returns:
    LevelInfo: An object containing the current level, remaining experience points, and experience points required for the next level.
    """
    curr_level = 0
    next_level_exp = INITIAL_LEVEL_EXP

    if exp >= 2_000_000:
        return LevelInfo(level=50, rem_exp=0, next_exp=0)

    while True:
        if exp >= next_level_exp:
            exp -= next_level_exp
            curr_level += 1
            next_level_exp = int(
                round(((next_level_exp * 0.2) + next_level_exp) / 10) * 10
            )
        else:
            break

    level_info = LevelInfo(level=curr_level, rem_exp=exp, next_exp=next_level_exp)
    return level_info
