from discord import ApplicationContext

from lib.exceptions.blacklist import UserBanned


def check_user(ctx: ApplicationContext | int):
    """
    Checks if the user is in the block list and raises UserBanned exception if they are.

    Args:
        ctx (Context): The context object containing information about the user.

    Raises:
        UserBanned: If the user is in the block list.

    Returns:
        None
    """
    if isinstance(ctx, int):
        if ctx in block_list:
            raise UserBanned()
    elif isinstance(ctx, ApplicationContext):
        if ctx.author.id in block_list:
            raise UserBanned()
    else:
        raise TypeError(f'ctx must be an instance of ApplicationContext or int, not {ctx.__class__.__name__}')


def load():
    with open('lib/blacklist/blacklist.txt', 'r') as f:
        raw_blacklist = f.read().strip().splitlines()
        return {int(i) for i in raw_blacklist}

block_list = load()

def add(i: int):
    block_list.add(i)
        
def delite(i: int):
    block_list.discard(i)

def write():
    with open('lib/blacklist/blacklist.txt', 'w') as f:
        for i in block_list:
            f.write(str(i) + '\n')

def reload():
    global block_list
    write()
    block_list = load()
