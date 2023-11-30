import os
import sys
from datetime import datetime

import elara

from lib.exceptions import database
from lib.utils.singleton_factory import singleton
from lib.settings.settings import Config


@singleton
class PlayersDB():
    def __init__(self) -> None:
        self.db = elara.exe('database/players.eldb')

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
                'nickname': nickname,
                'region': region,
                'premium': False,
                'premium_time': None,
                'lang': None,
                'last_stats': dict()
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

    def get_member(self, member_id: int) -> dict | None:
        member_id = str(member_id)

        if not self.check_member(member_id):
            return None
        else:
            return self.db['members'][member_id]
        
    def get_member_lang(self, member_id: int) -> str | None:
        member_id = str(member_id)

        if self.check_member(member_id):
            return self.db['members'][member_id]['lang']
        return None

    def delete_member_last_stats(self, member_id: int) -> None:
        member_id = str(member_id)
        del self.db['members'][member_id]['last_stats']
        self.db.commit()

    def delete_member(self, member_id: int):
        del self.db['members'][member_id]
        self.db.commit()

    def set_member_last_stats(self, member_id: int, data: dict) -> None:
        member_id = str(member_id)
        self.db['members'][member_id]['last_stats'] = data
        self.db.commit()

    def set_member_lang(self, member_id: int, lang: str | None):
        member_id = str(member_id)
        if self.check_member(member_id):
            self.db['members'][member_id]['lang'] = lang
            self.db.commit()
            return True
        else:
            return False

    def check_member_last_stats(self, member_id) -> bool:
        member_id = str(member_id)

        try:
            _ = self.db['members'][member_id]['last_stats']['timestamp']
        except (KeyError, TypeError):
            return False
        else:
            return True

    def get_member_last_stats(self, member_id) -> dict | None:
        member_id = str(member_id)
        if self._check_data_timestamp(member_id):
            if self.check_member_last_stats(member_id):
                return self.db['members'][member_id]['last_stats']

        return None
        
    def extend_session(self, member_id: int) -> None:
        member_id = str(member_id)
        if self.check_member(member_id) and self.check_member_last_stats(member_id):
            self.db['members'][member_id]['last_stats']['end_timestamp'] = \
                int(datetime.now().timestamp() + Config().get().session_ttl)
            self.db.commit()
        elif self.check_member(member_id) == None:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')
        elif self.check_member_last_stats(member_id) == None:
            raise database.LastStatsNotFound('Player last stats not found')
        
    def get_session_endtime(self, member_id: int) -> float | None:
        member_id = str(member_id)
        if self.check_member(member_id):
            if self.check_member_last_stats(member_id):
                return self.db['members'][member_id]['last_stats']['end_timestamp']
            else:
                raise database.LastStatsNotFound(f'Player last stats not found')
        else:
            raise database.MemberNotFound(f'Member not found, id: {member_id}')

    def _check_data_timestamp(self, member_id: int) -> bool:
        member = self.get_member(member_id)
        try:
            end_time = member['last_stats']['end_timestamp']
            if (end_time - datetime.now().timestamp()) < 0:
                self.delete_member_last_stats(member_id)
                return False
            return True
        
        except (KeyError, ValueError, AttributeError):
            return False