import os
import sys

from pymongo import MongoClient
from discord.ext.commands import Context

from lib.exceptions.database import ServerNotFound
from lib.settings.settings import Config
from lib.utils.singleton_factory import singleton


@singleton
class ServersDB():
    def __init__(self) -> None:
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['ServersDB']
        self.collection = self.db['servers']

    def set_new_server(self, server_id: int, server_name: str) -> None:
        server_id = str(server_id).strip()
        if self.collection.find_one() is None:
            self.collection.insert_one({
                'id': int(server_id),
                'name': server_name,
                'settings': dict(),
                'premium': False,
                'custom_background': None,
                'allow_user_backgrounds': True
            })
        
    def del_server_image(self, server_id: int) -> None:
        server_id = str(server_id)
        if self.check_server(server_id):
            self.collection.update_one(
                {'id': int(server_id)},
                {'$set': {'custom_background': None}}
            )
            
    def check_allow_backgrounds(self, server_id: int) -> bool:
        server_id = str(server_id)
        server = self.collection.find_one({'id': int(server_id)})
        if server and 'allow_user_backgrounds' in server:
            return server['allow_user_backgrounds']
        else:
            return True
        
    def check_server(self, server_id: int) -> bool:
        server_id = str(server_id)
        return self.collection.find_one({'id': int(server_id)}) is not None
        
    def get_server_image(self, server_id: int) -> str | None:
        server_id = str(server_id)
        server = self.collection.find_one({'id': int(server_id)})
        if server and 'custom_background' in server:
            return server['custom_background']
        else:
            return None
        
    def del_server(self, server_id: int) -> None:
        server_id = str(server_id)
        if self.check_server(server_id):
            self.collection.delete_one({'id': int(server_id)})
        
    def set_server_image(self, base64_image: str, ctx: Context):
        server_id = str(ctx.guild.id)
        if self.check_server(server_id):
            self.collection.update_one(
                {'id': int(server_id)},
                {'$set': {'custom_background': base64_image}}
            )
        else: 
            self.set_new_server(ctx.guild.id, ctx.guild.name)
            self.collection.update_one(
                {'id': int(server_id)},
                {'$set': {'custom_background': base64_image}}
            )
        
    def set_server_preium(self, server_id: int) -> None:
        if self.check_server(server_id):
            self.collection.update_one(
                {'id': int(server_id)},
                {'$set': {'premium': True}}
            )

    def unset_server_preium(self, server_id: int) -> None:
        if self.check_server(server_id):
            self.collection.update_one(
                {'id': int(server_id)},
                {'$set': {'premium': False}}
            )

    def check_server_premium(self, server_id: int) -> bool:
        server_id = str(server_id)
        server = self.collection.find_one({'id': int(server_id)})
        if server and 'premium' in server:
            return server['premium']
        else:
            return False