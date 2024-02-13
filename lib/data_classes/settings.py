from typing import List

from pydantic import BaseModel


class LogLevels(BaseModel):
    console: str
    file: str


class Logger(BaseModel):
    log_levels: LogLevels


class Server(BaseModel):
    host: str
    port: int


class Session(BaseModel):
    ttl: int


class Autosession(BaseModel):
    ttl: int


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


class Image(BaseModel):
    default_bg_path: str


class Internal(BaseModel):
    ignore_tankopedia_failures: bool


class HelpUrls(BaseModel):
    ru: str
    en: str
    ua: str


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
    logger: Logger
    bot_name: str
    server: Server
    session: Session
    autosession: Autosession
    default: Default
    image: Image
    internal: Internal
    help_urls: HelpUrls
    auth: Auth
    game_api: GameApi
    ds_api: DsApi
