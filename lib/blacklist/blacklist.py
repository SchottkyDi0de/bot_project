data = []

def load():
    with open('lib/blacklist/blacklist.txt', 'r') as f:
        raw_blacklist = f.read().strip().splitlines()
        for i in raw_blacklist:
            data.append(int(i))

load()

def write():
    with open('lib/blacklist/blacklist.txt', 'w') as f:
        for i in data:
            f.write(str(i) + '\n')

def reload():
    write()
    load()