import os
import sys
from threading import Thread
from datetime import datetime

import elara

if __name__ == '__main__':
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, path)

from lib.exceptions import database

class ServerDB():
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ServerDB, cls).__new__(cls)
        return cls.instance
    
    def __init__(self) -> None:
        self.db = elara.exe('database/serever_settings.eldb')
        self.defauls_server_settings = {
            'lang': 'eu',
            'search_reg' : 'eu',
        }
        
    def set_new_server(self, server_id: int, name: str):
        server_id = str(server_id)
        if self.db.get('servers') is None:
            self.db.hnew('servers')
            
        self.db.hadd(
            'servers', server_id, {
                'id': int(server_id),
                'name': name,
                'settings': self.defauls_server_settings,
                'premium': False
                }
            )
        self.db.commit()
        
    def check_server(self, server_id: int) -> bool:
        server_id = str(server_id)
        try:
            data = self.db.hget('servers', server_id)
        except (KeyError, TypeError):
            return False
        else:
            return data

    def set_member(self, member_id: int, nickname: str, region: str) -> None:
        member_id = str(member_id)
        
        if self.db.get('members') is None:
            self.db.hnew('members')
        
        if self.check_member(member_id):
            self.db['members'][member_id]['nickname'] = nickname
            self.db['members'][member_id]['region'] = region
        else:
            self.db['members'][member_id] = {
                'id': int(member_id),
                'nickname' : nickname,
                'region' : region,
                'premium' : False,
                'premium_time' : None,
                'last_stats' : dict()
            }
        self.db.commit()
        
    def check_member(self, member_id: int) -> bool:
        member_id = str(member_id)

        try:
            data = self.db['members'][member_id]
        except (KeyError, TypeError):
            return False
        else:
            if not data:
                return False
            return True
    
    def get_member(self, member_id: int) -> dict:
        member_id = str(member_id)

        if not self.check_member(member_id):
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        else:
            return self.db['members'][member_id]
        
    def delete_member_last_stats(self, member_id: int) -> None:
        member_id = str(member_id)
        del self.db['members'][member_id]['last_stats']
        self.db.commit()

    def get_server_lang(self, server_id):
        server_id = str(server_id)
        return self.db['servers'][server_id]['settings']['lang']
        
    def delete_member(self, member_id: int):
        del self.db['members'][member_id]
        self.db.commit()
        
    def set_region(self, server_id: int, region: str):
        server_id = str(server_id)
        self.db['servers'][server_id]['settings']['search_reg'] = region
        self.db.commit()
    
    def set_lang(self, server_id: int, lang: str):
        server_id = str(server_id)
        self.db['servers'][server_id]['settings']['lang'] = lang
        self.db.commit()
        
    def set_member_last_stats(self, member_id: int, data: dict):
        member_id = str(member_id)
        self.db['members'][member_id]['last_stats'] = data
        self.db.commit()
        
    def check_member_last_stats(self, member_id) -> bool:
        member_id = str(member_id)

        try:
            _ = self.db['members'][member_id]['last_stats']['timestamp']
        except (KeyError, TypeError):
            return False
        else:
            return True
        
    def get_member_last_stats(self, member_id) -> dict:
        self._check_data_timestamp(member_id)
        if self.check_member_last_stats(member_id):
            member_id = str(member_id)
            return self.db['members'][member_id]['last_stats']
        else:
            raise database.DatabaseError('Player last stats not found')
            
    def _check_data_timestamp(self, member_id: int) -> bool:
        now_time = datetime.now().timestamp()
        member = self.get_member(member_id)
        try:
            if (member['last_stats']['timestamp'] - now_time) > 43200:
                self.delete_member_last_stats(member_id)
        except (KeyError, ValueError, AttributeError) as e:
            raise database.LastStatsNotFound(e)
