# generated by datamodel-codegen:
#   filename:  settings.yaml
#   timestamp: 2024-09-03T08:52:58+00:00

from __future__ import annotations

from typing import List, Dict

from pydantic import BaseModel, Field


class Server(BaseModel):
    host: str
    port: str
    protocol: str


class Session(BaseModel):
    ttl: int


class Autosession(BaseModel):
    ttl: int


class Account(BaseModel):
    inactive_ttl: int


class Default(BaseModel):
    prefix: str
    lang: str
    available_locales: List[str]
    available_regions: List[str]
    locale_aliases: Dict[str, str]


class Image(BaseModel):
    default_bg_path: str
    available_stats: List[str]
    available_rating_stats: List[str]


class Themes(BaseModel):
    available: List[str]


class RegUrls(BaseModel):
    ru: str
    eu: str
    na: str
    asia: str


class Urls(BaseModel):
    get_id: str
    search: str
    get_stats: str
    get_achievements: str
    get_clan_stats: str
    get_tank_stats: str


class GameApi(BaseModel):
    reg_urls: RegUrls
    urls: Urls


class SessionWidget(BaseModel):
    url: str


class ConfigStruct(BaseModel):
    server: Server
    bot_name: str
    session: Session
    autosession: Autosession
    account: Account
    default: Default
    image: Image
    themes: Themes
    game_api: GameApi
    init_photos_id: int
    dump_export_to_id: int
    allowed_updates: List[str]
    developers_id: List[int]
    session_widget: SessionWidget
