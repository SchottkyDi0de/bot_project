from discord.ext.commands import Context
from lib.exceptions.blacklist import UserBanned

block_list = []

def check_user(ctx: Context):
    if ctx.author.id in block_list:
        raise UserBanned
    else:
        pass

def load():
    with open('lib/blacklist/blacklist.txt', 'r') as f:
        raw_blacklist = f.read().strip().splitlines()
        for i in raw_blacklist:
            block_list.append(int(i))

load()

def add(i: int):
    if i not in block_list:
        block_list.append(i)
        
def delite(i: int):
    if i in block_list:
        block_list.remove(i)

def write():
    with open('lib/blacklist/blacklist.txt', 'w') as f:
        for i in block_list:
            f.write(str(i) + '\n')

def reload():
    write()
    load()