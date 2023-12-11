from typing import List

from pydantic import BaseModel


class Server(BaseModel):
    host: str
    port: int


class LocaleAlliases(BaseModel):
    ru: str
    en: str
    pl: str
    uk: str


class Default(BaseModel):
    prefix: str
    lang: str
    available_locales: List[str]
    available_regions: List[str]
    locale_alliases: LocaleAlliases


class Internal(BaseModel):
    ignore_tankopedia_failures: bool


class Auth(BaseModel):
    wg_redirect_uri: str
    wg_uri: str
    ds_auth_redirect_url: str


class RegUrls(BaseModel):
    ru: str
    eu: str
    na: str
    asia: str


class Urls(BaseModel):
    get_id: str
    get_stats: str
    get_achievements: str
    get_clan_stats: str
    get_tank_stats: str


class GameApi(BaseModel):
    reg_urls: RegUrls
    urls: Urls


class Urls1(BaseModel):
    get_user: str


class DsApi(BaseModel):
    urls: Urls1


class ConfigStruct(BaseModel):
    bot_name: str
    server: Server
    session_ttl: int
    default: Default
    internal: Internal
    auth: Auth
    game_api: GameApi
    ds_api: DsApi