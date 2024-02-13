import traceback
import pytz
from datetime import datetime, timedelta

from pymongo import MongoClient
from pymongo.results import DeleteResult
from bson.codec_options import CodecOptions

from lib.data_classes.api.api_data import PlayerGlobalData
from lib.logger.logger import get_logger
from lib.data_classes.db_player import DBPlayer, ImageSettings, SessionSettings
from lib.exceptions import database
from lib.settings.settings import Config


_config = Config().get()
_log = get_logger(__file__, 'PlayersDBLogger', 'logs/players.log')


class PlayersDB:
    def __init__(self) -> None:
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['PlayersDB'].with_options(
            codec_options=CodecOptions(tz_aware=True)
        )
        self.collection = self.db['players']
        
        # self.database_update() # TODO: remove this

    def set_member(self, data: DBPlayer, override: bool = False) -> bool:
        ds_id = data.id
        if self.check_member(ds_id) and override:
            self.collection.update_one({'id': ds_id}, {'$set': {**(data.model_dump())}})
            return True
        elif self.collection.find_one({'id': ds_id}) is None:
            self.collection.insert_one(data.model_dump())
            return True
        else:
            return False
        
    def check_member(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        player = self.collection.find_one({'id': member_id})
        if player is not None:
            return True
        else:
            return False
        
    def get_players_ids(self) -> list:
        return [i['id'] for i in self.collection.find({})]
    
    def set_member_premium(self, member_id: int | str, time_secs: int = 2592000) -> bool:
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            self.collection.update_one(
                {'id': member_id}, 
                {'$set':
                        {
                        'premium': True,
                        'premium_time': int(datetime.now().timestamp()) + time_secs
                        }
                    }
                )
            return True
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')

        
    def unset_member_premium(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            self.collection.update_one(
                {'id': member_id}, 
                {'$set': 
                        {
                        'premium': False, 
                        'premium_time': None
                        }
                    }
                )
            return True
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')

        
    def check_member_is_verified(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            return self.collection.find_one({'id': member_id})['verified']
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')

        
    def check_member_premium(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        if self.check_member(member_id):
            player = self.collection.find_one({'id': member_id})
            premium = player['premium']
            premium_time = player['premium_time']
            if premium or premium_time is not None:
                if int(datetime.now().timestamp()) < self.collection.find_one({'id': member_id})['premium_time']:
                    return True
                else:
                    self.unset_member_premium(member_id)
            else:
                return False
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')

        
    def set_member_lock(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            self.collection.update_one(
                {'id': member_id}, 
                {'$set': 
                        {
                        'locked': True
                        }
                    }
                )
            return True
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')

        
    def unset_member_lock(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            self.collection.update_one(
                {'id': member_id}, 
                {'$set': 
                        {
                        'locked': False
                        }
                    }
                )
            return True
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        
    def check_member_lock(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            return self.collection.find_one({'id': member_id})['locked']
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        
    def set_image_settings(self, member_id: int | str, settings: ImageSettings):
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            self.collection.update_one(
                {'id': member_id}, 
                {'$set': 
                        {
                        'image_settings': settings.model_dump()
                        }
                    }
                )
            return True
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        
    def get_image_settings(self, member_id: int | str) -> ImageSettings:
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            field_exist = self.collection.find_one({'id': member_id, 'image_settings': {'$exists': True}}) is not None
            if field_exist:
                if self.collection.find_one({'id': member_id})['image_settings'] is not None:
                    return ImageSettings.model_validate(self.collection.find_one({'id': member_id})['image_settings'])
            else:
                self.set_image_settings(member_id, ImageSettings.model_validate({}))
                return ImageSettings.model_validate({})
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
    
    def set_member_image(self, member_id: int | str, image: str):
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            self.collection.update_one(
                {'id': member_id}, 
                {'$set': 
                        {
                        'image': image
                        }
                    }
                )
            return True
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        
    def get_member_image(self, member_id: int | str) -> str | None:
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            return self.collection.find_one({'id': member_id})['image']
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        
    def del_member_image(self, member_id: int | str):
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            self.collection.update_one(
                {'id': member_id}, 
                {'$set': 
                        {
                        'image': None
                        }
                    }
                )
            return True
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        
    def set_member_verified(self, member_id: int | str):
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            self.collection.update_one(
                {'id': member_id},
                {'$set': 
                        {
                        'verified': True
                        }
                    }
                )
            return True
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        
    def unset_member_verified(self, member_id: int | str):
        member_id = int(member_id)
        member_exist = self.check_member(member_id)
        if member_exist:
            self.collection.update_one(
                {'id': member_id}, 
                {'$set': 
                        {
                        'verified': False
                        }
                    }
                )
            return True
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
    
    def get_member(self, member_id: int | str) -> DBPlayer:
        member_id = int(member_id)
        data = self.collection.find_one({'id': member_id})
        if data is not None:
            del data['_id']
            return DBPlayer.model_validate(data)
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        
    def del_member(self, member_id: int) -> DeleteResult:
        member_id = int(member_id)
        return self.collection.delete_one({'id': member_id})
    
    def count_members(self) -> int:
        return self.collection.count_documents({})
        
    def set_member_lang(self, member_id: int | str, lang: str | None) -> bool:
        member_id = int(member_id)
        if self.check_member(member_id):
            self.collection.update_one(
                {'id': member_id}, 
                {'$set': 
                        {
                        'lang': lang
                        }
                    }
                )
            return True
        else:
            return False
        
    def set_member_last_stats(self, member_id: int | str, last_stats: dict):
        member_id = int(member_id)
        if self.check_member(member_id):
            self.collection.update_one(
                {'id': member_id}, 
                {'$set': 
                        {
                        'last_stats': last_stats,
                        }
                    }
                )
            return True
        else:
            return False
        
    def get_member_session_settings(self, member_id: int | str) -> SessionSettings:
        member_id = int(member_id)
        if self.check_member(member_id):
            data = self.collection.find_one({'id': member_id})
            return SessionSettings.model_validate(data['session_settings'])
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        
    def set_member_session_settings(self, member_id: int | str, session_settings: SessionSettings):
        member_id = int(member_id)
        if self.check_member(member_id):
            self.collection.update_one(
                {'id' : member_id}, {'$set' : {'session_settings' : session_settings.model_dump()}}
            )
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        
    # def check_member_session(self, member_id: int | str):
    #     member_id = int(member_id)
    #     try:
    #         if self.check_member(member_id):
    #             member = self.collection.find_one({'id': member_id})
    #             if member['last_stats'] is None:
    #                 raise database.LastStatsNotFound(f'Member last stats not found, member id: {member_id}')
    #             session_settings = self.get_member_session_settings(member_id)
    #             update_time = ...
    #     except Exception:
    #         _log.error(f'Database error: {traceback.format_exc()}')
    #         raise database.DatabaseError()

    def check_member_last_stats(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        if self.check_member(member_id):
            member = self.collection.find_one({'id': member_id})
            if member['last_stats'] is not None:
                return True  
            else:
                return False
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        
    def start_autosession(self, member_id: int | str, last_stats: PlayerGlobalData, session_settings: SessionSettings):
        member_id = int(member_id)
        
        self.set_member_last_stats(member_id, last_stats.model_dump())
        self.set_member_session_settings(member_id, session_settings)
        
    def validate_session(self, member_id: int | str):
        member_id = int(member_id)
        if self.check_member_last_stats(member_id):
            member_id = str(member_id)
            session_settings = self.get_member_session_settings(member_id)
            curr_time = datetime.now(pytz.utc)
            end_time = session_settings.last_get
            
            if end_time is None:
                return False
                
            if session_settings.is_autosession:
                end_time += timedelta(seconds=_config.autosession.ttl)
            else:
                end_time += timedelta(seconds=_config.session.ttl)
                
            if curr_time > end_time:
                self.reset_member_session(member_id)
                return False
            
            return True
        else:
            raise database.LastStatsNotFound(f'Last stats not found, id: {member_id}')
        
    def reset_member_session(self, member_id: int | str):
        member_id = int(member_id)
        if self.check_member(member_id):
            self.collection.update_one(
                {'id': member_id}, 
                {'$set': 
                        {
                        'last_stats': None
                        }
                    }
                )
            self.set_member_session_settings(member_id, SessionSettings.model_validate({}))
            return True
        else:
            return False
        
    def get_session_end_time(self, member_id: int | str) -> datetime:
        member_id = int(member_id)
        if self.check_member(member_id):
            if self.check_member_last_stats(member_id):
                session_settings = self.get_member_session_settings(member_id)
                if session_settings.is_autosession:
                    return session_settings.last_get + timedelta(seconds=_config.autosession.ttl)
                return session_settings.last_get + timedelta(seconds=_config.session.ttl)
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')

        
    def get_member_last_stats(self, member_id: int | str) -> PlayerGlobalData:
        member_id = int(member_id)
        if self.check_member(member_id):
            last_stats = self.collection.find_one({'id': member_id})['last_stats']
            if last_stats is not None:
                member = DBPlayer.model_validate(self.collection.find_one({'id': member_id}))
                member.session_settings.last_get = int(datetime.now(pytz.utc).timestamp())
                return PlayerGlobalData.model_validate(last_stats)
            else:
                raise database.LastStatsNotFound(f'Last stats not found, id: {member_id}')
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        
    def get_member_lang(self, member_id: int | str) -> str | None:
        if self.check_member(member_id):
            return self.collection.find_one({'id': member_id})['lang']
        else:
            return None
        
    # Run 1 time for update database structure...
    # def database_update(self):
    #     self.collection.update_many({}, {'$set' : {'image_settings' : ImageSettings().model_dump(), 'session_settings' : SessionSettings().model_dump()}})
    #     # self.collection.update_many({}, { '$set' :{ "last_stats" : None, "session_settings" : SessionSettings().model_dump()}})
    #     # self.collection.update_many(
    #     #     {}, { '$set' :{
    #     #             "image_settings.negative_stats_color" : '#c01515',
    #     #             "image_settings.positive_stats_color" : '#1eff26',
    #     #             }
    #     #         }
    #     #     )
    #     # self.collection.update_many({}, {'$set' : {'session_settings' : SessionSettings().model_dump()}})