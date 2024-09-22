from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Literal, Optional

import pytz
from pydantic import BaseModel

from lib.data_classes.api.api_data import PlayerGlobalData


class HookStatsTriggers(Enum):
    MORE_THAN = '>'
    MORE_OR_EQUAL = '>='
    LESS_THAN = '<'
    LESS_OR_EQUAL = '<='
    EQUAL_FOR = '=='
    NON_EQUAL = '!='
    

class HookWatchFor(Enum):
    MAIN = 'main'
    SESSION = 'session'
    DIFF = 'diff'


class BadgesEnum(Enum):
    premium = 0
    verified = 1
    active_user = 2
    streamer = 3
    theme_creator = 4
    docs_contributor = 5
    translator = 6
    beta_tester = 7
    tester = 8
    bug_hunter = 9
    admin = 10
    dev = 11

class SlotAccessState(Enum):
    empty_slot = 0
    used_slot = 1
    locked_slot = 2
    invalid_slot = 3


class StatsViewSettings(BaseModel):
    common_slots: dict = {
        'slot_1' : 'winrate',
        'slot_2' : 'avg_damage',
        'slot_3' : 'battles',
        'slot_4' : 'accuracy'
    }
    rating_slots: dict = {
        'slot_1' : 'winrate',
        'slot_2' : 'avg_damage',
        'slot_3' : 'battles',
        'slot_4' : 'rating'
    }


class SessionSettings(BaseModel):
    is_autosession: bool = False
    last_get: datetime = datetime.now(pytz.utc)
    timezone: int = 0
    time_to_restart: datetime = datetime.now(pytz.utc) + timedelta(days=1)


class ImageSettings(BaseModel):
    theme: str = 'default'
    colorize_stats: bool = True
    hide_nickname: bool = False
    hide_clan_tag: bool = False
    disable_flag: bool = False
    disable_rating_stats: bool = False
    disable_cache_label: bool = False
    disable_stats_blocks: bool = False
    stats_blocks_transparency: float = 0.5
    glass_effect: int = 5
    nickname_color: str = '#f0f0f0'  # Hex RGB Format #RRGGBB or #RGB
    clan_tag_color: str = '#0088fc'  # Hex validator: lib.image.utils.hex_color_validator
    stats_color: str = '#f0f0f0'
    main_text_color: str = '#0088fc'
    stats_text_color: str = '#0088fc'
    negative_stats_color: str = '#c01515'
    positive_stats_color: str = '#1eff26'


class WidgetSettings(BaseModel):
    disable_bg: bool = False
    disable_nickname: bool = False
    disable_main_stats_block: bool = False
    use_bg_for_stats_blocks: bool = True
    adaptive_width: bool = False
    max_stats_blocks: int = 1
    max_stats_small_blocks: int = 0
    update_time: int = 30  # Seconds
    background_transparency: float = 0.5
    stats_block_color: str = '#f0f0f0'

    @property
    def is_default(self) -> bool:
        return self == self.__class__()


class HookStats(BaseModel):
    active: bool = False
    stats_name: Optional[str] = None  # config.image -> available_stats or available_rating_stats accepted
    stats_type: Literal['common', 'rating'] = 'common'
    trigger: Optional[str] = None
    check_interval: int = 200
    end_time: datetime = datetime.now(pytz.utc) + timedelta(days=1)
    target_value: int | float | None = None
    target_nickname: Optional[str] = None
    target_region: Optional[str] = None
    last_stats: Optional[PlayerGlobalData] = None
    hook_target_member_id: Optional[int] = None
    hook_target_chat_id: Optional[int] = None
    watch_for: Literal['main', 'session', 'diff'] = 'main'
    try_dm_if_failure: bool = True
    lang: Optional[str] = None


class GameAccount(BaseModel):
    nickname: str
    game_id: int
    region: str
    last_stats: Optional[PlayerGlobalData] = None
    session_settings: SessionSettings = SessionSettings()
    image_settings: ImageSettings = ImageSettings()
    widget_settings: WidgetSettings = WidgetSettings()
    stats_view_settings: StatsViewSettings = StatsViewSettings()
    verified: bool = False
    locked: bool = False


def set_widget_settings(**kwargs) -> WidgetSettings:
    '''
    Setup widget settings from kwargs
    If value is None, it will be ignored
    '''
    return WidgetSettings(**{k: v for k, v in kwargs.items() if v is not None})
    

def set_image_settings(**kwargs) -> ImageSettings:
    '''
    Setup image settings from kwargs
    If value is None, it will be ignored
    '''
    return ImageSettings(**{k: v for k, v in kwargs.items() if v is not None})


class AccountSlotsEnum(Enum):
    slot_1 = 1
    slot_2 = 2
    slot_3 = 3
    slot_4 = 4
    slot_5 = 5


class SessionStatesEnum(Enum):
    NORMAL = 0
    RESTART_NEEDED = 1
    NOT_STARTED = 2
    EXPIRED = 3


class GameAccounts(BaseModel):
    slot_1: Optional[GameAccount] = None
    slot_2: Optional[GameAccount] = None
    slot_3: Optional[GameAccount] = None
    slot_4: Optional[GameAccount] = None
    slot_5: Optional[GameAccount] = None

    def get_account_by_slot(self, slot: str | AccountSlotsEnum) -> GameAccount:
        if isinstance(slot, AccountSlotsEnum):
            slot = slot.name
        return getattr(self, slot)
    
    def as_list(self) -> List[GameAccount]:
        dat = []
        for i in range(1, 6):
            slot_val = getattr(self, f'slot_{i}')
            if slot_val is not None:
                dat.append(slot_val)
        return dat

    def as_dict(self) -> Dict[str, GameAccount | None]:
        dat = {}
        for i in range(1, 6):
            slot_str = f'slot_{i}'
            dat[slot_str] = getattr(self, slot_str)
        return dat

class UsedCommand(BaseModel):
    name: str
    last_used: datetime

class Profile(BaseModel):
    premium: bool = False
    premium_time: Optional[datetime] = None
    badges: List[str] = []
    used_commands: List[UsedCommand] = []
    level_exp: int = 0
    last_activity: datetime = datetime.now(pytz.utc)
    commands_counter: int = 0

class DBPlayer(BaseModel):
    id: int
    lang: Optional[str] = None
    image: Optional[str] = None
    use_custom_image: bool = True
    game_accounts: GameAccounts
    profile: Profile
    current_game_account: str = AccountSlotsEnum.slot_1.name
    hook_stats: HookStats = HookStats()

    @property
    def current_account(self) -> GameAccount:
        return self.game_accounts.get_account_by_slot(slot=self.current_game_account)
    
    @property
    def current_slot(self) -> AccountSlotsEnum:
        return getattr(AccountSlotsEnum, self.current_game_account)
    
    @property
    def has_more_than_one_account(self) -> bool:
        return len(self.game_accounts.as_list()) > 1
    
    @property
    def not_almsman(self) -> bool:
        return self.profile.premium
