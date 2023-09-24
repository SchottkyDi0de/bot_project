blacklist = []

with open('lib/blacklist/blacklist.txt', 'r') as f:
    raw_blacklist = f.read().strip().splitlines()
    for i in raw_blacklist:
        blacklist.append(int(i))