from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from lib.data_classes.tankopedia import Tank
from lib.logger import logger
from lib.utils.singleton_factory import singleton

_log = logger.get_logger(__file__, 'TankopediaLogger', 'logs/tankopedia.log')


@singleton
class TankopediaDB:
    def __init__(self) -> None:
        self.client = AsyncIOMotorClient("mongodb://localhost:27017")
        self.sync_client = MongoClient('mongodb://localhost:27017/')
        
        self.db = self.client['TankopediaDB']
        self.sync_db = self.sync_client['TankopediaDB']
        
        self.collection_eu_sync = self.sync_db.get_collection('tanks_eu')
        self.collection_ru_sync = self.sync_db.get_collection('tanks_ru')
        
        self.collection_ru = self.db.get_collection('tanks_ru')
        self.collection_eu = self.db.get_collection('tanks_eu')
        
    async def get_tank_by_id(self, id: int | str, region: str) -> Tank | None:
        id = int(id)
        
        if region == 'ru':
            data = await self.collection_ru.find_one({'id': id})
        else:
            data = await self.collection_eu.find_one({'id': id})
            
        if data is None:
            return data
        
        return Tank().model_validate(data)
    
    def get_tank_by_id_sync(self, id: int | str, region: str) -> Tank | None:
        id = int(id)
        
        if region == 'ru':
            data = self.collection_ru_sync.find_one({'id': id})
        else:
            data = self.collection_ru_sync.find_one({'id': id})
            
        if data is None:
            _log.warn(f"TankopediaDB: tank with id {id} not found in {region} region")
            return data
        
        return Tank().model_validate(data)
    
    async def set_tank(self, tank: Tank, region: str):
        if region == 'ru':
            await self.collection_ru.update_one({'id': tank.id}, {'$set': tank.model_dump()}, upsert=True)
        else:
            await self.collection_eu.update_one({'id': tank.id}, {'$set': tank.model_dump()}, upsert=True)
            
    async def set_tanks(self, tanks: list[Tank], region: str):
        if region == 'ru':
            for tank in tanks:
                await self.collection_ru.update_one({'id': tank.id}, {'$set': tank.model_dump()}, upsert=True)
        else:
            for tank in tanks:
                await self.collection_eu.update_one({'id': tank.id}, {'$set': tank.model_dump()}, upsert=True)

    async def del_tank(self, id: int | str, region: str):
        id = int(id)
        
        if region == 'ru':
            await self.collection_ru.delete_one({'id': id})
        else:
            await self.collection_eu.delete_one({'id': id})
