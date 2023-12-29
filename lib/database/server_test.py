from pymongo import MongoClient
from pprint import pprint
from time import sleep

class PlayersDB:
    def __init__(self) -> None:
        self.client = MongoClient('mongodb://localhost:27017/')
        self.collection = self.client['PlayersDB']
        self.db = self.collection['players']

    def set_member(self, member_id: int, stats: dict) -> None:
        self.db.insert_one({'id': member_id, 'stats': stats})
    
    def get_member(self, member_id: int) -> dict:
        return self.db.find_one({'id': member_id})
    
    def loop_check(self):
        while True:
            try:
                for i in self.db.find():
                    pprint(i)
                sleep(.5)
            except KeyboardInterrupt:
                self.client.close()
                quit(0)
        
        
db = PlayersDB()
db.loop_check()