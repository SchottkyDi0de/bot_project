import os
import sys

import elara
from discord.ext.commands import Context
from discord.ext.commands import Context

from lib.exceptions.database import ServerNotFound
from lib.settings.settings import Config
from lib.utils.singleton_factory import singleton


@singleton
class ServersDB():
    def __init__(self) -> None:
        self.db = elara.exe('database/servers.eldb')
        try:
            self.db.db['servers']
        except KeyError:
            self.db.hnew('servers')

    def set_new_server(self, server_id: int, server_name: str) -> None:
        server_id = str(server_id)
        if self.db.get('servers') is None:
            self.db.hnew('servers')
            
        self.db.hadd(
            'servers',
            server_id, {
                'id': int(server_id),
                'name': server_name,
                'settings': dict(),
                'premium': False,
                'custom_background': None
                'settings': dict(),
                'premium': False,
                'custom_background': None
                }
            )
        self.db.commit()
        
    def check_server(self, server_id: int) -> bool:
        server_id = str(server_id)
        try:
            _ = self.db.db['servers'][server_id]
        except (KeyError, AttributeError):
            return False
        else:
            return True
        
    def get_server_image(self, server_id: int) -> str | None:
        server_id = str(server_id)
        if self.check_server(server_id):
            return self.db['servers'][server_id]['custom_background']
        else:
            return None
        
    def del_server(self, server_id: int) -> None:
        server_id = str(server_id)
        if self.check_server(server_id):
            del self.db['servers'][server_id]
        self.db.commit()
        
    def set_server_image(self, base64_image: str, ctx: Context):
        server_id = str(ctx.guild.id)
        if self.check_server(server_id):
            self.db['servers'][server_id]['custom_background'] = base64_image
        else: 
            self.set_new_server(ctx.guild.id, ctx.guild.name)
            self.db['servers'][str(server_id)]['custom_background'] = base64_image
        
        self.db.commit()

    def set_server_preium(self, server_id: int) -> None:
        if self.check_server(server_id):
            self.db['servers'][server_id]['premium'] = True

        self.db.commit()

    def unset_server_preium(self, server_id: int) -> None:
        if self.check_server(server_id):
            self.db['servers'][server_id]['premium'] = False

        self.db.commit()

    def check_server_premium(self, server_id: int) -> bool:
        server_id = str(server_id)
        if self.check_server(server_id):
            return self.db['servers'][server_id]['premium']
        else:
            return False
