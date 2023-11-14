from typing import List

from pydantic import BaseModel


class Leagues(BaseModel):
    gold: str
    platinum: str
    brilliant: str
    no_league: str
    calibration: str


class ForImage(BaseModel):
    main: str
    winrate: str
    avg_damage: str
    battles: str
    medals: str
    mainGun: str
    medalKolobanov: str
    warrior: str
    medalRadleyWalters: str
    markOfMastery: str
    rating: str
    personal_rating: str
    rating_battles: str
    no_rating: str
    tank: str
    leagues: Leagues
    total: str
    kills_per_battle: str
    max_frags: str
    enemies_destroyed: str
    destruction_ratio: str
    damage_caused: str
    damage_ratio: str
    average_spotted: str
    battles_survived: str
    all_xp: str
    max_xp: str
    shots: str
    accuracy: str
    no_clan: str
    no_data: str


class MapNames(BaseModel):
    desert_sands: str
    middleburg: str
    copperfield: str
    alpenstadt: str
    mines: str
    dead_rail: str
    fort_despair: str
    himmelsdorf: str
    black_goldville: str
    basis_palm: str
    ghost_factory: str
    molendijk: str
    port_bay: str
    winter_malinovka: str
    castilia: str
    canal: str
    vineyards: str
    yamato_harbor: str
    canyon: str
    mayan_ruins: str
    dynasty_pearl: str
    naval_frontier: str
    falls_creek: str
    new_bay: str
    normandy: str
    wasteland: str
    unknown: str


class Gamemodes(BaseModel):
    any: str
    regular: str
    training_room: str
    tournament: str
    quick_tournament: str
    rating: str
    mad_games: str
    realistic_battles: str
    urprising: str
    gravity_mode: str
    skirmish: str
    burning_games: str
    unknown: str


class Errors(BaseModel):
    error: str
    unknown_error: str
    user_banned: str
    api_error: str
    parser_error: str


class Info(BaseModel):
    info: str
    player_not_registred: str
    err_info_sent: str


class TimeUnits(BaseModel):
    h: str
    m: str
    s: str


class Common(BaseModel):
    nickname: str
    region: str
    time_units: TimeUnits


class Frequent(BaseModel):
    errors: Errors
    info: Info
    common: Common


class Descr(BaseModel):
    this: str
    sub_descr: str


class Errors1(BaseModel):
    player_not_found: str


class Info1(BaseModel):
    player_not_registred: str


class Astats(BaseModel):
    descr: Descr
    errors: Errors1
    info: Info1
    items: str


class SubDescr(BaseModel):
    nickname: str
    region: str


class Descr1(BaseModel):
    this: str
    sub_descr: SubDescr


class Errors2(BaseModel):
    player_not_found: str
    no_battles: str
    uncorrect_nickname: str


class Stats(BaseModel):
    descr: Descr1
    errors: Errors2
    info: str
    items: str


class SubDescr1(BaseModel):
    nickname: str
    region: str


class Descr2(BaseModel):
    this: str
    sub_descr: SubDescr1


class Errors3(BaseModel):
    player_not_found: str


class Info2(BaseModel):
    set_player_ok: str


class SetPlayer(BaseModel):
    descr: Descr2
    errors: Errors3
    info: Info2
    items: str


class SubDescr2(BaseModel):
    lang_list: str
    to_server: str


class Descr3(BaseModel):
    this: str
    sub_descr: SubDescr2


class Errors4(BaseModel):
    player_not_registred: str
    permission_denied: str


class Info3(BaseModel):
    set_lang_ok: str


class SetLang(BaseModel):
    descr: Descr3
    errors: Errors4
    info: Info3


class Descr4(BaseModel):
    this: str
    sub_descr: str


class Errors5(BaseModel):
    session_not_found: str


class Info4(BaseModel):
    player_not_registred: str


class Items(BaseModel):
    started: str
    not_started: str


class SessionState(BaseModel):
    descr: Descr4
    errors: Errors5
    info: Info4
    items: Items


class Descr5(BaseModel):
    this: str
    sub_descr: str


class Errors6(BaseModel):
    session_not_found: str
    session_not_updated: str


class Info5(BaseModel):
    player_not_registred: str


class GetSession(BaseModel):
    descr: Descr5
    errors: Errors6
    info: Info5
    items: str


class Descr6(BaseModel):
    this: str
    sub_descr: str


class Info6(BaseModel):
    player_not_registred: str
    started: str


class StartSession(BaseModel):
    descr: Descr6
    errors: str
    info: Info6
    items: str


class Descr7(BaseModel):
    this: str
    sub_descr: str


class Errors7(BaseModel):
    session_not_found: str


class Info7(BaseModel):
    session_extended: str
    player_not_registred: str


class ExtendSession(BaseModel):
    descr: Descr7
    errors: Errors7
    info: Info7
    items: str


class SubDescr3(BaseModel):
    help_types: str


class Descr8(BaseModel):
    this: str
    sub_descr: SubDescr3


class Info8(BaseModel):
    send_ok: str


class Items1(BaseModel):
    help: str
    help_types: List[str]
    syntax: str
    setup: str
    statistics: str
    session: str
    other: str


class Help(BaseModel):
    descr: Descr8
    errors: str
    info: Info8
    items: Items1


class SubDescr4(BaseModel):
    file: str


class Descr9(BaseModel):
    this: str
    sub_descr: SubDescr4


class Errors8(BaseModel):
    parsing_error: str
    uncorrect_file_format: str

class Common1(BaseModel):
    win: str
    lose: str

class Items2(BaseModel):
    avg_stats: str
    empty_player: str
    title: str
    description: str
    common: Common1


class ParseReplay(BaseModel):
    descr: Descr9
    errors: Errors8
    info: str
    items: Items2


class Cmds(BaseModel):
    astats: Astats
    stats: Stats
    set_player: SetPlayer
    set_lang: SetLang
    session_state: SessionState
    get_session: GetSession
    start_session: StartSession
    help: Help
    parse_replay: ParseReplay


class Localization(BaseModel):
    for_image: ForImage
    frequent: Frequent
    map_names: MapNames
    gamemodes: Gamemodes
    cmds: Cmds