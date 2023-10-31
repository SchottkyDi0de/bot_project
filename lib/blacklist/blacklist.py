from discord.ext.commands import Context
from lib.exceptions.blacklist import UserBanned

def check_user(ctx: Context):
    if ctx.author.id in block_list:
        raise UserBanned
    else:
        pass

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
