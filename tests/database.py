import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
import elara
import json

db = db = elara.exe('database/serever_settings.eldb')

def db_to_json():
    with open('database_copy.json', 'w') as f:
        f.write(json.dumps(db['members'], indent=4))

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
    timestamp_check_all()