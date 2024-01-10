import traceback
from pprint import pprint, PrettyPrinter
import time

from pymongo import MongoClient
from pymongo.results import DeleteResult
from lib.logger.logger import get_logger
from lib.data_classes.db_player import DBPlayer, ImageSettings, SessionSettings
from datetime import datetime
from lib.exceptions import database
from lib.settings.settings import Config


_config = Config().get()
_log = get_logger(__name__, 'PlayersDBLogger', 'logs/playersdb.log')


class PlayersDB:
    def __init__(self) -> None:
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['PlayersDB']
        self.collection = self.db['players']

    def set_member(self, data: DBPlayer, override: bool = False) -> bool:
        data = DBPlayer.model_dump(data)
        if self.check_member(data['id']) and override:
            self.collection.update_one({'id': data['id']}, {'$set': {**data}})
            return True
        elif self.collection.find_one({'id': data['id']}) is None:
            self.collection.insert_one({'id': data['id'], **data})
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
        try:
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
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def unset_member_premium(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        try:
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
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def check_member_is_verefied(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        try:
            member_exist = self.check_member(member_id)
            if member_exist:
                return self.collection.find_one({'id': member_id})['verified']
            else:
                raise database.MemberNotFound(f'Member not found, id: {member_id}')
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def check_member_premium(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        try:
            if self.check_member(member_id):
                player = self.collection.find_one({'id': member_id})
                premium = player['premium']
                premium_time = player['premium_time']
                if premium and premium_time is not None:
                    if int(datetime.now().timestamp()) < self.collection.find_one({'id': member_id})['premium_time']:
                        return True
                    else:
                        self.unset_member_premium(member_id)
                else:
                    return False
            else:
                raise database.MemberNotFound(f'Member not found, id: {member_id}')
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def set_member_lock(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        try:
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
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def unset_member_lock(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        try:
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
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def check_member_lock(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        try:
            member_exist = self.check_member(member_id)
            if member_exist:
                return self.collection.find_one({'id': member_id})['locked']
            else:
                raise database.MemberNotFound(f'Member not found, id: {member_id}')
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def set_image_settings(self, member_id: int | str, settings: ImageSettings):
        member_id = int(member_id)
        try:
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
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def get_image_settings(self, member_id: int | str) -> ImageSettings:
        member_id = int(member_id)
        try:
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
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
    
    def set_member_image(self, member_id: int | str, image: str):
        member_id = int(member_id)
        try:
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
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def get_member_image(self, member_id: int | str) -> str | None:
        member_id = int(member_id)
        try:
            member_exist = self.check_member(member_id)
            if member_exist:
                return self.collection.find_one({'id': member_id})['image']
            else:
                raise database.MemberNotFound(f'Member not found, id: {member_id}')
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return None
        
    def del_member_image(self, member_id: int | str):
        member_id = int(member_id)
        try:
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
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def set_member_verified(self, member_id: int | str):
        member_id = int(member_id)
        try:
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
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def unset_member_verified(self, member_id: int | str):
        member_id = int(member_id)
        try:
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
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
    
    def get_member(self, member_id: int) -> DBPlayer | None:
        data = self.collection.find_one({'id': member_id})
        if data is not None:
            del data['_id']
            return DBPlayer.model_validate(data)
        else:
            return None
        
    def del_member(self, member_id: int) -> DeleteResult:
        member_id = int(member_id)
        return self.collection.delete_one({'id': member_id})
    
    def count_members(self) -> int:
        return self.collection.count_documents({})
        
    def set_member_lang(self, member_id: int | str, lang: str | None) -> bool:
        member_id = int(member_id)
        try:
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
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def set_member_last_stats(self, member_id: int | str, last_stats: dict):
        member_id = int(member_id)
        try:
            if self.check_member(member_id):
                self.collection.update_one(
                    {'id': member_id}, 
                    {'$set': 
                            {
                            'last_stats': last_stats
                            }
                        }
                    )
                return True
            else:
                return False
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def session_settings_checker(self, member_id: int | str) -> bool:
        if self.check_member(member_id):
            if self.collection.find_one({'id': member_id})['session_settings'] is not None:
                return True
        else:
            return False
        
    def autosession_handler(self, member_id: int | str) -> bool:
        pass
    
    def get_member_autosession(self, member_id: int | str) -> SessionSettings:
        pass
        
    def check_member_last_stats(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        try:
            if self.check_member(member_id):
                member = self.collection.find_one({'id': member_id})
                if member['last_stats'] is not None:
                    if member['last_stats']['end_timestamp'] is not None:
                        curr_time = int(datetime.now().timestamp())
                        end_time = int(member['last_stats']['end_timestamp'])
                        if end_time > curr_time:
                            return True
                        else:
                            self.del_member_last_stats(member_id)
                else:
                    return False
            else:
                raise database.MemberNotFound(f'Member not found, id: {member_id}')
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
    def del_member_last_stats(self, member_id: int | str):
        member_id = int(member_id)
        try:
            if self.check_member(member_id):
                self.collection.update_one(
                    {'id': member_id}, 
                    {'$set': 
                            {
                            'last_stats': None
                            }
                        }
                    )
                return True
            else:
                return False
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False
        
        
    def get_session_end_time(self, member_id: int | str) -> int | None:
        member_id = int(member_id)
        try:
            if self.check_member(member_id):
                if self.check_member_last_stats(member_id):
                    return self.collection.find_one({'id': member_id})['last_stats']['end_timestamp']
            else:
                return None
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return None
        
    def get_member_last_stats(self, member_id: int | str) -> dict | None:
        member_id = int(member_id)
        try:
            if self.check_member(member_id):
                return self.collection.find_one({'id': member_id})['last_stats']
            else:
                return None
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return None
        
    def get_member_lang(self, member_id: int | str) -> str | None:
        member_id = int(member_id)
        try:
            if self.check_member(member_id):
                return self.collection.find_one({'id': member_id})['lang']
            else:
                return None
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return None
        
    def extend_session(self, member_id: int | str) -> bool:
        member_id = int(member_id)
        try:
            if self.check_member(member_id):
                if self.check_member_last_stats(member_id):
                    user = self.collection.find_one({'id': member_id})
                    user['last_stats']['end_timestamp'] = int(datetime.now().timestamp()) + _config.session.ttl
                    self.collection.update_one(
                        {'id': member_id},
                        {'$set': user}
                        )
                else:
                    raise database.LastStatsNotFound(f'Last stats for user: {member_id} not found')
                return True
            else:
                raise database.MemberNotFound(f'Member not found, id: {member_id}')
        except Exception:
            _log.error(f'Database error: {traceback.format_exc()}')
            return False