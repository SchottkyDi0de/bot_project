from uuid import uuid4
from time import time
from typing import TYPE_CHECKING

from lib.exceptions.cooldown import CooldownError

if TYPE_CHECKING:
    from aiogram.types import Message, CallbackQuery


class MemberCooldown:
    def __init__(self, cooldown_time: int) -> None:
        self.last_used = time()
        self.cooldown_time = cooldown_time
    
    @property
    def update_limit(self):
        waiting_time = time() - self.last_used
        
        if waiting_time > self.cooldown_time:
            self.last_used = time()
            return True
        
        exc = CooldownError()
        exc.wait = round(self.cooldown_time - waiting_time, 1)
        raise exc

    @property
    def check_limit(self):
        waiting_time = time() - self.last_used

        if waiting_time > self.cooldown_time:
            return True

        raise CooldownError


class GroupStorage:
    def __init__(self, group_cooldown_time: int) -> None:
        self.storage: dict[int, MemberCooldown] = {}
        self.group_cooldown_time = group_cooldown_time
    
    def __getitem__(self, user_id: int) -> bool:
        try:
            return self.storage[user_id].update_limit
        except KeyError:
            self.storage[user_id] = MemberCooldown(self.group_cooldown_time)
            return True
    
    def update_limit(self, user_id: int) -> bool:
        return self[user_id]
    
    def clear_storage(self):
        for user_id in [*self.storage]:
            try:
                self.storage[user_id].check_limit
            except CooldownError:
                ...
            else:
                del self.storage[user_id]


class CooldownStorage:
    storage: dict[str, GroupStorage] = {}

    def __class_getitem__(cls, group_name: str) -> GroupStorage:
        return cls.storage[group_name]

    @classmethod
    def cooldown(cls, cooldown_time: int, group_name: str | None = None):
        def inner(func):
            if group_name is None:
                code = str(uuid4())
                while code in cls.storage: code = str(uuid4())
                gname = code
            else:
                gname = group_name

            if gname not in cls.storage:
                cls.storage[gname] = GroupStorage(cooldown_time)
            
            async def wrapper(self, data: 'Message | CallbackQuery', *args, **kwargs):
                storage: GroupStorage = cls[gname]
                storage.update_limit(data.from_user.id)
                return await func(self, data, *args, **kwargs)

            return wrapper
        return inner
