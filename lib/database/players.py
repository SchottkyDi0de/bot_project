from datetime import datetime, timedelta
from asyncio import sleep
from random import randint
from types import NoneType
from typing import Literal

from motor import MotorCursor
import pytz
import motor.motor_asyncio
from bson.codec_options import CodecOptions

from lib.data_classes.api.api_data import PlayerGlobalData
from lib.data_classes.db_player import (
    DBPlayer, 
    ImageSettings,
    SessionSettings, 
    StatsViewSettings, 
    WidgetSettings,
    GameAccount,
    Profile,
    SessionStatesEnum,
    AccountSlotsEnum,
    UsedCommand,
)
from lib.data_classes.db_player_old import DBPlayerOld
from lib.exceptions import database
from lib.logger.logger import get_logger
from lib.settings.settings import Config
from lib.utils.calculate_exp import exp_calc
from lib.utils.singleton_factory import singleton

_config = Config().get()
_log = get_logger(__file__, 'PlayersDBLogger', 'logs/players_db.log')


@singleton
class PlayersDB:
    def __init__(self) -> None:
        self.client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
        self.db = self.client['PlayersDB']
        self.collection = self.db.get_collection('players', codec_options=CodecOptions(tz_aware=True, tzinfo=pytz.utc))
    
    async def _multi_args_member_checker(self, member_id: int | str | None = None, member: DBPlayer | None = None) -> DBPlayer:
        """
        Check if the given member ID and member object are valid and return the appropriate member object.

        Args:
            member_id (int): The ID of the member.
            member (DBPlayer): The member object.

        Raises:
            ValueError: If neither member ID nor member object is provided.

        Returns:
            DBPlayer: The member object if it is not None, otherwise the member object retrieved from the database using the member ID.

        """
        if (member_id is None) and (member is None):
            raise ValueError('You must provide either id or member')
        
        return member if member is not None else await self.get_member(member_id)
        
    async def create_index_for_id(self):
        """
        Asynchronously creates an index on the 'id' field of the collection.

        This function creates a unique index on the 'id' field of the collection. The index is used to improve the performance of queries that involve the 'id' field.

        Parameters:
            self (PlayersDB): The instance of the PlayersDB class.

        Returns:
            None
            
        Note:
            Use one time only.
        """
        await self.collection.create_index({'id': 1}, unique=True)
        
    async def get_all_members_count(self) -> int:
        """
        Asynchronously retrieves the count of all documents in the collection.

        This function uses the `count_documents` method of the `collection` attribute to 
        retrieve the count of all documents in the collection. The count is obtained by 
        passing an empty filter `{}` to the method.

        Returns:
            int: The count of all documents in the collection.
        """
        return await self.collection.count_documents({})
    
    async def count_sessions(self) -> int:
        sessions = 0
        cursor = self.collection.find({})

        while cursor.alive:
            member = DBPlayer.model_validate(await cursor.next())
            all_slots = await self.get_all_used_slots(member=member)
            for slot in all_slots:
                if await self.check_member_last_stats(member=member, slot=slot):
                    sessions += 1
        
        return sessions

    async def get_all_members_ids(self) -> list[int]:
        """
        Asynchronously retrieves a list of all unique member IDs from the collection.

        This function uses the `distinct` method of the `collection` attribute to retrieve
        a list of all unique values for the 'id' field in the collection. The result is a
        list of member IDs.

        Returns:
            list: A list of unique member IDs.
        """
        return await self.collection.distinct('id')
    
    async def set_member(self, slot: AccountSlotsEnum, member_id: int | str, game_account: GameAccount, slot_override: bool = False) -> None:
        """
        Sets a member's game account in the specified slot or creates a new member if it doesn't exist.

        Args:
            member_id (int | str): The ID of the member.
            game_account (GameAccount): The game account to set.
            slot (AccountSlotsEnum, optional): The slot to set the game account in. Defaults to AccountSlotsEnum.slot_1.
            slot_override (bool, optional): Whether to override the slot if it's not empty. Defaults to False.

        Raises:
            TypeError: If the slot is not an instance of AccountSlotsEnum.

        Returns:
            None
        """
        if not isinstance(slot, AccountSlotsEnum):
            raise TypeError(f'slot must be an instance of AccountSlotsEnum, not {slot.__class__.__name__}')
        
        member_id = int(member_id)
        member = await self.check_member_exists(member_id=member_id, raise_error=False, get_if_exist=True)
        
        if not isinstance(member, bool):
            await self.check_access_to_slot(slot, member=member)
            slot_is_empty = await self.check_slot_empty(slot, member=member, raise_error=False)
            if slot_is_empty or slot_override:
                await self.collection.update_one(
                    {'id': member_id},
                    {'$set': {f'game_accounts.{slot.name}': game_account.model_dump()}}
                )
        else:
            await self.collection.insert_one({
                'id': member_id,
                'lang' : None,
                'image' : None,
                'game_accounts':{
                    'slot_1': game_account.model_dump(),
                    'slot_2': None,
                    'slot_3': None,
                    'slot_4': None,
                    'slot_5': None
                },
                'profile': Profile().model_dump(),
                'current_game_account': AccountSlotsEnum.slot_1.name
            })
        
            
    async def get_member(self, member_id: int | str) -> DBPlayer:
        """
        Asynchronously retrieves a member from the database based on their ID.

        Args:
            member_id (int | str): The ID of the member to retrieve.

        Returns:
            DBPlayer: The member object if it exists in the database, None otherwise.
        """
        member: DBPlayer = await self.check_member_exists(member_id=member_id, get_if_exist=True)
        return member
    
    async def validate_slot(self, slot: AccountSlotsEnum | None, member_id: int | str | None = None, member: DBPlayer | None = None, allow_empty: bool = False) -> AccountSlotsEnum:
        """
        Asynchronously validates a slot for a given member.

        Args:
            member_id (int | str | None): The ID of the member.
            member (DBPlayer | None, optional): The member object. Defaults to None.
            slot (AccountSlotsEnum | None, optional): The slot to validate. Defaults to None.
            allow_empty (bool, optional): Whether to allow empty slots. Defaults to False.

        Returns:
            AccountSlotsEnum: The validated slot.

        Raises:
            database.SlotIsEmpty: If the slot is empty and allow_empty is False.
        """
        if slot is None:
            return await self.get_current_game_slot(member_id=member_id, member=member)
        
        member = await self._multi_args_member_checker(member_id, member)
        await self.check_access_to_slot(slot, member=member)
        
        empty_slot = await self.check_slot_empty(slot, member=member, raise_error=False)
        if not allow_empty and empty_slot:
            _log.debug(f'Member {member.id} has attempted to access empty slot {slot.name}')
            raise database.SlotIsEmpty(f'Member {member.id} has attempted to access empty slot {slot.name}')
        
        
        return slot
    
    async def get_game_account(self, slot: AccountSlotsEnum, member_id: int | str | None = None, member: DBPlayer | None = None) -> GameAccount:
        member = await self._multi_args_member_checker(member_id, member)
        slot = await self.validate_slot(member=member, slot=slot)
        game_account = getattr(member.game_accounts, slot.name)
        if game_account is None:
            _log.warn(f'Member {member_id} has no game account in slot {slot.name}')
            raise database.SlotIsEmpty(f'Member {member_id} has no game account in slot {slot.name}')
        else:
            return game_account
    
    async def delete_member(self, member_id: int | str) -> None:
        """
        Asynchronously deletes a member from the database based on their ID.

        Args:
            member_id (int | str): The ID of the member to delete.

        Returns:
            None: This function does not return anything.
        """
        await self.collection.delete_one({'id': member_id})
        
    async def check_member_exists(self, member_id: int | str, get_if_exist: bool = False, raise_error: bool = True) -> bool | DBPlayer:
        """
        Asynchronously checks if a player with the given ID exists in the database.

        Parameters:
            id (int | str): The ID of the player to check.
            get_if_exist (bool, optional): If True, returns the player object if it exists. Defaults to False.
            raise_error (bool, optional): If True, raises a MemberNotFound exception if the player does not exist. Defaults to True.

        Returns:
            bool | DBPlayer: If get_if_exist is False, returns True if the player exists, False otherwise.
            If get_if_exist is True, returns the player object if it exists, False otherwise.

        Raises:
            MemberNotFound: If raise_error is True and the player does not exist.
        """
        member_id = int(member_id)
        result = await self.collection.find_one({'id': member_id})
        
        if raise_error and result is None:
            _log.error(f'Player with id {member_id} not found')
            raise database.MemberNotFound()
        
        if get_if_exist:
            if result is not None:
                player = DBPlayer.model_validate(result)
                return player
            else:
                return False
        else:
            return True if result is not None else False
    
    async def check_access_to_slot(self, slot: AccountSlotsEnum, member_id: int | str = None, member: DBPlayer = None) -> None:
        """
        Check if a member has access to a specific slot.

        Args:
            slot (AccountSlotsEnum): The slot to check access for.
            member_id (int | str, optional): The ID of the member. Defaults to None.
            member (DBPlayer, optional): The member object. Defaults to None.

        Raises:
            database.PremiumSlotAccessAttempt: If the member is not premium and tries to access a premium slot.
        """
        member = await self._multi_args_member_checker(member_id, member)
        premium = await self.check_premium(member_id, member)
        
        if slot.value > 2:
            if not premium:
                _log.info(f'Member is not premium and tried to access premium slot {slot.value}')
                raise database.PremiumSlotAccessAttempt(f'Member is not premium and tried to access premium slot {slot.value}')
            
    async def check_slot_empty(self, slot: AccountSlotsEnum, member_id: int | str | None = None, member: DBPlayer | None = None, raise_error: bool = True) -> bool:
        """
        Check if the specified slot is empty for a given member.

        Args:
            slot (AccountSlotsEnum): The slot to check for emptiness.
            member_id (int | str, optional): The ID of the member. Defaults to None.
            member (DBPlayer, optional): The member object. Defaults to None.
            raise_error (bool, optional): Whether to raise an exception if the slot is not empty.
            Defaults to True.

        Returns:
            bool: True if the slot is empty, False otherwise.

        Raises:
            database.SlotIsNotEmpty: If the slot is not empty and raise_error is True.
        """
        member = await self._multi_args_member_checker(member_id, member)
        
        if getattr(member.game_accounts, slot.name) is not None:
            if raise_error:
                _log.warn(f'Member tried to access not empty slot {slot.value}')
                raise database.SlotIsNotEmpty()
            else:
                return False
        else:
            return True
        
    async def unset_premium(self, member_id: int | str) -> None:
        """
        Unsets the premium status of a member in the database.

        Args:
            id (int | str): The ID of the member.

        Returns:
            None

        Raises:
            None

        This function updates the 'profile.premium' and 'profile.premium_time' fields of the member with the given ID in the database. It sets 'profile.premium' to False and 'profile.premium_time' to None, effectively unsetting the premium status of the member.
        """
        member = await self.check_member_exists(member_id, get_if_exist=True)
        curr_slot = await self.get_current_game_slot(member=member)
        if curr_slot.value > 2:
            await self.set_current_account(member_id=member.id, slot=AccountSlotsEnum.slot_1)
        
        await self.collection.update_one(
            {'id': member.id}, 
            {'$set': {'profile.premium': False, 'profile.premium_time': None}}
        )
        
    async def set_premium(self, member_id: int | str, end_time: datetime | None) -> None:
        """
        Sets the premium status of a member in the database.

        Args:
            id (int | str): The ID of the member.
            end_time (datetime | None): The end time of the member's premium status. If None, the member will be set as premium indefinitely.

        Returns:
            None

        Raises:
            None

        This function updates the 'profile.premium' and 'profile.premium_time' fields of the member with the given ID in the database. If 'end_time' is None, the member will be set as premium indefinitely. Otherwise, the member will be set as premium until the specified 'end_time'.
        """
        _log.info(f'Setting premium for id {member_id}, end_time: {end_time}')
        end_time = datetime.now(pytz.utc) + timedelta(days=14) if end_time is None else end_time
        await self.collection.update_one(
            {'id': member_id},
            {'$set': {'profile.premium': True, 'profile.premium_time': end_time}}
        )
        
    async def check_premium(self, member_id: int | str | None = None, member: DBPlayer | None = None) -> bool:
        """
        Check if a member is premium or not.

        Args:
            member_id (int | str): The ID of the member. If None, the member object must be provided.
            member (DBPlayer): The member object. If None, the member_id must be provided.

        Returns:
            bool: True if the member is premium, False otherwise.

        Raises:
            ValueError: If neither member_id nor member is provided.

        This function checks if a member is premium or not. It takes either a member_id or a member object as input.
        If both are provided, the member_id is ignored. If neither is provided, a ValueError is raised.

        The function first checks if the member is premium by retrieving the member object using the member_id.
        If the member is premium, it checks if the premium_time is None. If it is None, the member is considered premium.
        If the premium_time is not None, it checks if the current datetime is before the premium_time. If it is, the member is considered premium.
        If the current datetime is after the premium_time, the member's premium status is unset and False is returned.

        If the member is not premium, False is returned.
        """
        member = await self._multi_args_member_checker(member_id, member)
        
        premium = member.profile.premium
        premium_time = member.profile.premium_time
        
        if premium:
            if premium_time is None:
                return True
            else:
                if datetime.now(pytz.utc) < premium_time:
                    return True
                else:
                    _log.debug(f'Unset premium for member {member.id}')
                    await self.unset_premium(member.id)
                    return False
        else:
            return False

    async def get_current_game_account(self, member_id: int | str | None = None, member: DBPlayer | None = None) -> GameAccount:
        member = await self._multi_args_member_checker(member_id, member)
        game_account: GameAccount | None = getattr(member.game_accounts, member.current_game_account)
        if game_account is None:
            _log.warn(f'Member {member.id} has no game account in slot {member.current_game_account}')
            raise database.SlotIsEmpty(f'Member {member.id} has no game account in slot {member.current_game_account}')
        else:
            return game_account

    async def get_current_game_slot(self, member_id: int | str | None = None, member: DBPlayer | None = None) -> AccountSlotsEnum:
        member = await self._multi_args_member_checker(member_id, member)
        return AccountSlotsEnum[member.current_game_account]
        
    async def start_session(self, slot: AccountSlotsEnum, member_id: int | str, last_stats: PlayerGlobalData, session_settings: SessionSettings) -> None:
        member = await self.check_member_exists(member_id, get_if_exist=True)
        slot = await self.validate_slot(member=member, slot=slot)
        await self.collection.update_one(
            {'id': member_id},
            {'$set': 
                {
                    f'game_accounts.{slot.name}.last_stats': last_stats.model_dump(),
                    f'game_accounts.{slot.name}.session_settings': session_settings.model_dump(),
                }
            },
        )
    
    async def find_account_by_params(
            self,
            nickname: str,
            region: str,
            member_id: int | str | None = None,
            member: DBPlayer | None = None,
        ) -> GameAccount | None:
        member = self._multi_args_member_checker(member_id, member)
        game_accounts = member.game_accounts
        used_slots: list[AccountSlotsEnum] = await self.get_all_used_slots(member=member)
        if used_slots is None:
            return None
        
        for slot in used_slots:
            if getattr(game_accounts, slot.name).nickname.lower() == nickname.lower():
                if getattr(game_accounts, slot.name).region == region:
                    return getattr(game_accounts, slot.name)
        
        return None
        
    async def get_session_settings(self, slot: AccountSlotsEnum, member_id: int | str, member: DBPlayer) -> SessionSettings:
        member = await self._multi_args_member_checker(member_id, member)
        slot = await self.validate_slot(member=member, slot=slot)
        return getattr(member.game_accounts, slot.name).session_settings
    
    async def get_image_settings(self, slot: AccountSlotsEnum, member_id: int | str | None = None, member: DBPlayer | None = None) -> ImageSettings:
        member = await self._multi_args_member_checker(member_id, member)
        slot = await self.validate_slot(member=member, slot=slot)
        return getattr(member.game_accounts, slot.name).image_settings
    
    async def get_last_stats(self, slot: AccountSlotsEnum, member_id: int | str | None = None, member: DBPlayer | None = None) -> PlayerGlobalData:
        member = await self._multi_args_member_checker(member_id, member)
        slot = await self.validate_slot(member=member, slot=slot)
        last_stats = getattr(member.game_accounts, slot.name).last_stats
        if last_stats is None:
            _log.warn(f'Member {member.id} has no last stats in slot {slot.name}')
            raise database.LastStatsNotFound(f'Member {member.id} has no last stats in slot {slot.name}')
        else:
            return PlayerGlobalData.model_validate(last_stats)
        
    async def get_stats_view_settings(self, slot: AccountSlotsEnum, member_id: int | str | None = None, member: DBPlayer | None = None) -> StatsViewSettings:
        member = await self._multi_args_member_checker(member_id, member)
        slot = await self.validate_slot(member=member, slot=slot)
        return getattr(member.game_accounts, slot.name).stats_view_settings

    async def get_widget_settings(self, slot: AccountSlotsEnum, member_id: int | str | None = None, member: DBPlayer | None = None) -> WidgetSettings:
        member = await self._multi_args_member_checker(member_id, member)
        slot = await self.validate_slot(member=member, slot=slot)
        return getattr(member.game_accounts, slot.name).widget_settings
    
    async def stop_session(self, slot: AccountSlotsEnum, member_id: int | str) -> None:
        slot = await self.validate_slot(member_id=member_id, slot=slot)
        await self.collection.update_one(
            {'id': member_id},
            {'$set': {f'game_accounts.{slot.name}.last_stats': None}}
        )
    
    async def check_member_last_stats(self, slot: AccountSlotsEnum, member_id: int | str | None = None, member: DBPlayer | None = None) -> bool:
        member = await self._multi_args_member_checker(member_id, member)
        slot = await self.validate_slot(member=member, slot=slot)
        game_account: GameAccount = getattr(member.game_accounts, slot.name)
        last_stats = game_account.last_stats
        session_settings = game_account.session_settings
        if last_stats is None:
            return False
        else:
            if session_settings.last_get + timedelta(seconds=_config.session.ttl) < datetime.now(pytz.utc):
                await self.stop_session(slot=slot, member_id=member.id)
                return False
            else:
                return True
            
    async def session_restart_needed(self, slot: AccountSlotsEnum, member_id: int | str | None = None, member: DBPlayer | None = None) -> bool:
        member = await self._multi_args_member_checker(member_id, member)
        slot = await self.validate_slot(member=member, slot=slot)
        game_account: GameAccount = getattr(member.game_accounts, slot.name)
        session_settings = game_account.session_settings
        if not session_settings.is_autosession:
            return False
        elif session_settings.time_to_restart > datetime.now(pytz.utc):
            return True
        else:
            return False
        
    async def validate_session(self, slot: AccountSlotsEnum, member_id: int | str | None = None, member: DBPlayer | None = None) -> SessionStatesEnum:
        member = await self._multi_args_member_checker(member_id, member)
        last_stats = await self.check_member_last_stats(slot, member=member)
        if not last_stats:
            return SessionStatesEnum.NOT_STARTED
        if await self.session_restart_needed(slot=slot, member=member):
            return SessionStatesEnum.RESTART_NEEDED
        else:
            return SessionStatesEnum.NORMAL
        
    async def update_session(
            self,
            slot: AccountSlotsEnum,
            member_id: int | str,
            session_settings: SessionSettings,
            last_stats: PlayerGlobalData, 
        ) -> None:
        member = await self._multi_args_member_checker(member_id, None)
        curr_slot = await self.get_current_game_slot(member_id, member) if slot is None else slot
        restart_time = session_settings.time_to_restart + timedelta(days=1)
        session_settings.time_to_restart = restart_time
        await self.collection.update_one(
            {'id': member_id},
            {'$set': 
                {
                    f'game_accounts.{curr_slot.name}.last_stats': last_stats.model_dump(), 
                    f'game_accounts.{curr_slot.name}.session_settings': session_settings.model_dump(),
                }
            }
        )
        
    async def get_all_used_slots(self, member_id: int | str | None = None, member: DBPlayer | None = None) -> list[AccountSlotsEnum]:
        member = await self._multi_args_member_checker(member_id, member)
        premium_user = await self.check_premium(member_id, member)
        slots = []
        
        for slot in AccountSlotsEnum:
            if not await self.check_slot_empty(member=member, slot=slot, raise_error=False):
                slots.append(slot)
                
            if slot.value > 2 and not premium_user:
                break
        
        return slots
    
    async def get_lang(self, member_id: int | str | None = None, member: DBPlayer | None = None) -> str | None:
        member = await self.collection.find_one({'id': member_id})
        return DBPlayer.model_validate(member).lang if member is not None else None
    
    async def set_lang(self, member_id: int | str, lang: str | None) -> None:
        """
        Asynchronously sets the language of a member in the database.

        Args:
            member_id (int | str): The ID of the member.
            lang (str | None): The language to set. If None, the language field will be set to None.

        Returns:
            None: This function does not return anything.

        This function updates the 'lang' field of the member with the given ID in the database. If the language is None, it sets the language field to None.
        """
        await self.collection.update_one(
            {'id': member_id},
            {'$set': {'lang': lang}}
        )
    
    async def check_member_is_verified(self, slot: AccountSlotsEnum, member_id: int | str | None = None, member: DBPlayer | None = None) -> bool:
        member = await self._multi_args_member_checker(member_id, member)
        slot = await self.validate_slot(member=member, slot=slot)
        return getattr(member.game_accounts, slot.name).verified
    
    async def set_member_lock(self, slot: AccountSlotsEnum, member_id: int | str, lock: bool) -> None:
        member = await self.check_member_exists(member_id, get_if_exist=True)
        slot = await self.validate_slot(slot=slot, member=member)
        await self.collection.update_one(
            {'id': member_id},
            {'$set': {f'game_accounts.{slot.name}.lock': lock}}
        )
    
    async def set_image(self, member_id: int | str, image: str | None) -> None:
        """
        Asynchronously sets the image of a member in the database.

        Args:
            member_id (int | str): The ID of the member.
            image (str | None): Base64 encoded image. If None, the image field will be set to None.

        Returns:
            None: This function does not return anything.

        This function updates the 'image' field of the member with the given ID in the database. If the image is None, it sets the image field to None.
        """
        if not isinstance(image, (str, NoneType)):
            raise TypeError(f'image must be either a string or None, not {image.__class__.__name__}')
        
        if isinstance(image, str):
            if len(image) == 0:
                image = None
        
        await self.check_member_exists(member_id)
        await self.collection.update_one(
            {'id': member_id},
            {'$set': {'image': image}}
        )
        
    async def set_stats_view_settings(self, slot: AccountSlotsEnum | None, member_id: int | str, settings: StatsViewSettings) -> None:
        member = await self.check_member_exists(member_id, get_if_exist=True)
        slot = await self.validate_slot(member=member, slot=slot)
        await self.collection.update_one(
            {'id': member_id},
            {'$set': {f'game_accounts.{slot.name}.stats_view_settings': settings.model_dump()}}
        )
        
    async def set_image_settings(self, slot: AccountSlotsEnum | None, member_id: int | str, settings: ImageSettings) -> None:
        member = await self.check_member_exists(member_id, get_if_exist=True)
        slot = await self.validate_slot(member=member, slot=slot)
        await self.collection.update_one(
            {'id': member_id},
            {'$set': {f'game_accounts.{slot.name}.image_settings': settings.model_dump()}}
        )
        
    async def get_member_image(self, member_id: int | str | None, member: DBPlayer | None) -> str | None:
        member = await self._multi_args_member_checker(member_id, member)
        return member.image
    
    async def set_session_settings(self, slot: AccountSlotsEnum, member_id: int | str, settings: SessionSettings) -> None:
        member = await self.check_member_exists(member_id, get_if_exist=True)
        slot = await self.validate_slot(member=member, slot=slot)
        await self.collection.update_one(
            {'id': member_id},
            {'$set': {f'game_accounts.{slot.name}.session_settings': settings.model_dump()}}
        )
        
    async def get_session_end_time(self, slot: AccountSlotsEnum, member_id: int | str | None = None, member: DBPlayer | None = None) -> datetime:
        member = await self._multi_args_member_checker(member_id, member)
        slot = await self.validate_slot(member=member, slot=slot)
        game_account = await self.get_game_account(slot, member=member)
        return game_account.session_settings.last_get + timedelta(seconds=_config.session.ttl)
    
    async def set_widget_settings(self, slot: AccountSlotsEnum, member_id: int | str, settings: WidgetSettings) -> None:
        member = await self.check_member_exists(member_id, get_if_exist=True)
        slot = await self.validate_slot(member=member, slot=slot)
        await self.collection.update_one(
            {'id': member_id},
            {'$set': {f'game_accounts.{slot.name}.widget_settings': settings.model_dump()}}
        )
        
    async def set_current_account(self, member_id: int | str, slot: AccountSlotsEnum) -> None:
        member = await self.check_member_exists(member_id, get_if_exist=True)
        slot = await self.validate_slot(member=member, slot=slot)
        await self.collection.update_one(
            {'id': member_id},
            {'$set': {'current_game_account': slot.name}}
        )
        
    async def set_verification(self, member_id: int | str, slot: AccountSlotsEnum, verified: bool) -> None:
        member = await self.check_member_exists(member_id, get_if_exist=True)
        slot = await self.validate_slot(member=member, slot=slot)
        await self.collection.update_one(
            {'id': member_id},
            {'$set': {f'game_accounts.{slot.name}.verified': verified}}
        )
        
    async def set_last_activity(self, member_id: int | str, time: datetime = datetime.now(pytz.utc)) -> None:
        await self.collection.update_one(
            {'id': member_id},
            {'$set': {'profile.last_activity': time}}
        )
    
    async def get_last_activity(self, member_id: int | str | None = None, member: DBPlayer | None = None) -> datetime:
        member = await self._multi_args_member_checker(member_id, member)
        return member.profile.last_activity
        
    async def get_analytics(self, member_id: int | str | None = None, member: DBPlayer | None = None, raw: bool = False) -> list[UsedCommand] | list[dict]:
        member = await self._multi_args_member_checker(member_id, member)
        if len(member.profile.used_commands) == 0:
            return []
        
        if raw:
            return [UsedCommand.model_dump(used_command) for used_command in member.profile.used_commands]
    
        return member.profile.used_commands
        
    async def set_analytics(self, analytics: UsedCommand, member: DBPlayer | None = None, member_id: int | str | None = None) -> None:
        member = await self._multi_args_member_checker(member_id, member)
        used_commands: list[dict] = await self.get_analytics(member=member, raw=True)
        
        if len(used_commands) >= 10:
            used_commands.pop(0)
            
        used_commands.append(analytics.model_dump())
        last_activity = datetime.now(pytz.utc)
        
        level_exp = exp_calc(analytics.name)
        
        await self.collection.update_one(
            {'id': member.id},
            {'$set': {
                'profile.used_commands': used_commands, 
                'profile.last_activity': last_activity,
                'profile.commands_counter' : member.profile.commands_counter + 1,
                'profile.xp' : member.profile.level_exp + level_exp
                }
            }
        )

    async def database_update(self):
        cursor = self.collection.find({})
        async for member in cursor:
            try:
                old_member = DBPlayerOld.model_validate(member)
            except Exception:
                continue
            
            new_member = {
                '_id' : member['_id'],
                'id': old_member.id,
                'lang' : old_member.lang,
                'image': old_member.image,
                'use_custom_bg': old_member.image_settings.use_custom_bg,
                'game_accounts': {
                    'slot_1' : {
                        'nickname' : old_member.nickname,
                        'game_id' : old_member.game_id,
                        'region' : old_member.region,
                        'last_stats' : old_member.last_stats,
                        'session_settings' : old_member.session_settings.model_dump(),
                        'image_settings' : old_member.image_settings.model_dump(),
                        'widget_settings' : old_member.widget_settings.model_dump(),
                        'stats_view_settings' : old_member.session_settings.stats_view.model_dump(),
                        'verified' : old_member.verified,
                        'locked' : old_member.locked,
                    },
                    'slot_2' : None,
                    'slot_3' : None,
                    'slot_4' : None,
                    'slot_5' : None,
                },
                'profile': Profile.model_validate({}),
                'current_game_account': 'slot_1',
            }
            try:
                data = DBPlayer.model_validate(new_member).model_dump()
            except ValueError:
                new_member['game_accounts']['slot_1']['last_stats'] = None
                data = DBPlayer.model_validate(new_member).model_dump()
            
            await self.collection.replace_one(
                {'id': old_member.id},
                replacement=data
            )
            
            _log.debug(f'DB: Player {old_member.id} updated')
            await sleep(0.01)
