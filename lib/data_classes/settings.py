from typing import Dict, List

from pydantic import BaseModel


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
    locale_aliases: Dict


class Image(BaseModel):
    default_bg_path: str
    available_stats: List[str]
    available_rating_stats: List[str]


class Themes(BaseModel):
    available: List[str]


class Internal(BaseModel):
    ignore_tankopedia_failures: bool


class HelpUrls(BaseModel):
    ru: str
    en: str
    ua: str
    pl: str


class SessionWidget(BaseModel):
    url: str


class Auth(BaseModel):
    wg_redirect_uri: str
    wg_uri: str
    ds_auth_redirect_url: str
    ds_auth_primary_uri: str


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


class Urls1(BaseModel):
    get_user: str


class DsApi(BaseModel):
    urls: Urls1


class Report(BaseModel):
    suggestion_channel_id: int
    bug_channel_id: int


class Dump(BaseModel):
    export_to_id: int
    chunk_size: int
    directory: str


class PassedServer(BaseModel):
    id: int
    premium_roles: List[int]


class PayLinks(BaseModel):
    da: str
    boosty: str


class Premium(BaseModel):
    passed_server: PassedServer
    pay_links: PayLinks


class ConfigStruct(BaseModel):
    bot_name: str
    server: Server
    session: Session
    autosession: Autosession
    account: Account
    default: Default
    image: Image
    themes: Themes
    internal: Internal
    help_urls: HelpUrls
    session_widget: SessionWidget
    auth: Auth
    game_api: GameApi
    ds_api: DsApi
    report: Report
    dump: Dump
    premium: Premium
