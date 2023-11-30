# Посмотри на pytest для автоматических тестов:
# https://docs.pytest.org/en/7.4.x/

import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
import elara
import json

db = elara.exe('database/players.eldb')
sdb = elara.exe('database/servers.eldb')
tdb = elara.exe('database/tankopedia.eldb')

def db_to_json(db_name: str = 'players'):
    db_name += '.json'
    with open(db_name, 'w', encoding='utf-8') as f:
        f.write(json.dumps(db['members'], indent=4))
        print('database written to json')
    
def sdb_to_json(db_name: str = 'servers'):
    db_name += '.json'
    with open(db_name, 'w', encoding='utf-8') as f:
        f.write(json.dumps(sdb['servers'], indent=4))
        print('database written to json')

def tdb_to_json(db_name: str = 'tankopedia'):
    db_name += '.json'
    with open(db_name, 'w', encoding='utf-8') as f:
        f.write(json.dumps(tdb['root']['id_list'], indent=4))
        print('database written to json')

def members_count():
    print(f'Registered members count: {db.db["members"].keys().__len__()}')

def timestamp_check_all():
    full_time_format = '%Y.%m.%d [%H:%M:%S]'
    timestamp_format = '[%H:%M:%S]'
    for i, j in enumerate(db.db["members"]):
        if db['members'][j]['last_stats'] == {}:
            continue
        else:
            timestamp = db['members'][j]['last_stats']['timestamp']
            expiried_at = 43200 - (datetime.now().timestamp() - timestamp)

            if expiried_at < 0:
                expiried_at = datetime.utcfromtimestamp(-expiried_at).strftime(timestamp_format) + " Timestamp Expiried!"
            else:
                expiried_at = datetime.utcfromtimestamp(expiried_at).strftime(timestamp_format)

            print(f"\n\
Timestamp: {datetime.utcfromtimestamp(timestamp).strftime(full_time_format)}\n\
User_id: {j}\n\
User_game_nickname: {db['members'][j]['nickname']}\n\
Expiried at: {expiried_at}")


if __name__ == '__main__':
    sdb_to_json('servers')
