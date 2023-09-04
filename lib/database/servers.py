import os
import sys
from datetime import datetime
from lib.exceptions.database import ServerNotFound

import elara


class ServersDB():
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ServersDB, cls).__new__(cls)
        return cls.instance
    
    def __init__(self) -> None:
        self.db = elara.exe('database/servers.eldb')
        self.defauls_server_settings = {
            'lang': 'en',
            'is_premium': False
        }
        try:
            self.db.db['servers']
        except KeyError:
            self.db.hnew('servers')

    def set_new_server(self, server_id: int, server_name: str) -> None:
        server_id = str(server_id)
        if self.db.get('servers') is None:
            self.db.hnew('servers')
            
        self.db.hadd(
            'servers', server_id, {
                'id': int(server_id),
                'name': server_name,
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
            return True
        
    def set_lang(self, server_id: int, lang: str, server_name: str) -> None:
        server_id = str(server_id)
        if self.check_server(server_id):
            self.db.db['servers'][server_id]['settings']['lang'] = lang
            self.db.commit()
        else:
            self.set_new_server(server_id, server_name)
            self.db.db['servers'][server_id]['settings']['lang'] = lang
            self.db.commit()

    def get_lang(self, server_id: int):
        server_id = str(server_id)
        if self.check_server(server_id):
            return self.db.db['servers'][server_id]['settings']['lang']
        else:
            raise ServerNotFound('Get lang error, server not found in database')
        
    def safe_get_lang(self, server_id: int):
        server_id = str(server_id)
        if self.check_server(server_id):
            return self.db.db['servers'][server_id]['settings']['lang']
        else:
            return 'en'