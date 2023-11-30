import os
import sys

import elara

from lib.exceptions.database import ServerNotFound
from lib.settings.settings import Config
from lib.utils.singleton_factory import singleton


@singleton
class ServersDB():
    def __init__(self) -> None:
        self.db = elara.exe('database/servers.eldb')
        self.defauls_server_settings = {
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
