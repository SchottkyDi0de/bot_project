data = {
    '432' : {
        'id' : 432,
        'stats' : 44.2,
        'diff_battles' : 2
    },
    '44' : {
        'id' : 44,
        'stats' : 24.2,
        'diff_battles' : 1
    },
    '2234' : {
        'id' : 2234,
        'stats' : 28.2,
        'diff_battles' : 5
    },
    '4433' : {
        'id' : 4433,
        'stats' : 64.2,
        'diff_battles' : 8
    }
}
    
iterator = iter(data)
while True:
    
    try:
        print(next(iterator))
    except StopIteration:
        print('stop')
        break
    