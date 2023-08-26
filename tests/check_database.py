import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

import elara
import json

def print_db():
    db = elara.exe('database/serever_settings.eldb')
    with open('database_copy.json', 'w') as f:
        f.write(json.dumps(db['members'], indent=4))

if __name__ == '__main__':
    print_db()