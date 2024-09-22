from typing import List

from io import BytesIO

from pydantic import BaseModel
from cacheout import Cache
from aiogram.types import Message

from .db_player import ImageSettings, WidgetSettings, StatsViewSettings, SessionSettings
from .replay_data_parsed import ParsedReplayData, Player
from lib.utils.stats_preview import StatsPreview, SVPreview
from lib.utils.delete_message import DeleteMessage


class _Interface(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    delete_messages: DeleteMessage

    def __init__(self, *args, **kwargs):
        kwargs |= {"delete_messages": DeleteMessage()}
        super().__init__(*args, **kwargs)


class ImageSettingsStateData(_Interface):
    author_id: int
    stats_preview: StatsPreview
    base_image_settings: ImageSettings
    current_image_settings: ImageSettings
    is_changed: bool = False
    resetted: bool = False
    color_of_what: str | None = None
    main_message: None | Message = None
    colors_message: None | Message = None
    others_message: None | Message = None
    other_change_param: None | str = None
    last_generated_image_settings: ImageSettings | None = None
    image: None | BytesIO | str = None



class WidgetSettingsStateData(_Interface):
    base_widget_settings: WidgetSettings
    current_widget_settings: WidgetSettings
    main_message: None | Message = None
    changing_param_name: str | None = None
    resetted: bool = False
    
    @property
    def is_settings_changed(self) -> bool:
        return self.current_widget_settings != self.base_widget_settings


class SVSettingsStateData(_Interface):
    base_sv_settings: StatsViewSettings
    current_sv_settings: StatsViewSettings
    last_generated_sv_settings: StatsViewSettings | None = None
    preview: SVPreview | None = None
    slot_num: int | None = None
    rating: bool = False

    @property
    def is_changed(self) -> bool:
        return self.current_sv_settings != self.base_sv_settings

    @property
    def need_regenerate(self) -> bool:
        return self.last_generated_sv_settings != self.current_sv_settings


class ReplayParserStateData(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    region: str
    cache: Cache
    replay_data: ParsedReplayData
    team1: List[Player]
    team2: List[Player]

    def __init__(self, *args, **kwargs):
        kwargs |= {"cache": Cache()}
        super().__init__(*args, **kwargs)


class SessionStateData(BaseModel):
    session_settings: SessionSettings

    def __init__(self, *args, **kwargs):
        kwargs |= {"session_settings": SessionSettings()}
        super().__init__(*args, **kwargs)
