import pytz
import motor.motor_asyncio
from bson.codec_options import CodecOptions

from lib.logger.logger import get_logger
from lib.utils.singleton_factory import singleton

_log = get_logger(__file__, 'InternalDBLogger', 'logs/internal_db.log')


@singleton
class InternalDB():
    def __init__(self) -> None:
        self.client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
        self.db = self.client.get_database('InternalDB')
        self.collection = self.db.get_collection('internal', codec_options=CodecOptions(tz_aware=True, tzinfo=pytz.utc))
        
    async def set_actual_premium_users(self, users: list[int]) -> None:
        if await self.collection.find_one({'name': 'internal_info'}) is None:
            await self.collection.insert_one(
                {'name': 'internal_info', 'premium_users': users},
            )
        else:
            await self.collection.update_one(
                {'name': 'internal_info'},
                {'$set': {'premium_users': users}},
            )
        
    async def get_actual_premium_users(self) -> list[int]:
        data = await self.collection.find_one({'name': 'internal_info'})
        return data['premium_users'] if data is not None else []