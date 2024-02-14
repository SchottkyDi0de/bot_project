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
    rockfield: str
    desert_sands: str
    middleburg: str
    copperfield: str
    alpenstadt: str
    mines: str
    dead_rail: str
    fort_despair: str
    himmelsdorf: str
    black_goldville: str
    oasis_palm: str
    ghost_factory: str
    molendijk: str
    port_bay: str
    winter_malinovka: str
    castilia: str
    canal: str
    vineyards: str
    canyon: str
    mayan_ruins: str
    dynasty_pearl: str
    naval_frontier: str
    falls_creek: str
    new_bay: str
    normandy: str
    yamato_harbor: str
    wasteland: str
    lagoon: str
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
    warning: str


class TimeUnits(BaseModel):
    d: str
    h: str
    m: str
    s: str


class Common(BaseModel):
    yes: str
    no: str
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
    uncorrect_nickname: str
    no_battles: str


class Stats(BaseModel):
    descr: Descr1
    errors: Errors2
    info: str
    items: str


class Descr2(BaseModel):
    this: str
    sub_descr: SubDescr


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


class Errors6(BaseModel):
    session_not_found: str
    session_not_updated: str


class GetSession(BaseModel):
    descr: Descr4
    errors: Errors6
    info: Info4
    items: str


class Info6(BaseModel):
    player_not_registred: str
    started: str


class StartSession(BaseModel):
    descr: Descr4
    errors: str
    info: Info6
    items: str


class SubDescr3(BaseModel):
    timezone: str
    restart_time: str


class Descr7(BaseModel):
    this: str
    sub_descr: SubDescr3


class Errors7(BaseModel):
    uncorrect_r_time: str


class StartAutosession(BaseModel):
    descr: Descr7
    errors: Errors7
    info: Info6
    items: str


class SubDescr4(BaseModel):
    image: str
    server: str
    resize_mode: str


class Descr8(BaseModel):
    this: str
    sub_descr: SubDescr4


class Errors8(BaseModel):
    player_not_registred: str
    permission_denied: str
    file_error: str
    oversize: str
    overresolution: str
    small_resolution: str


class Info8(BaseModel):
    set_background_ok: str


class SetBackground(BaseModel):
    descr: Descr8
    errors: Errors8
    info: Info8
    items: str


class SubDescr5(BaseModel):
    use_custom_bg: str
    glass_effect: str
    blocks_bg_brightness: str
    nickname_color: str
    clan_tag_color: str
    stats_color: str
    main_text_color: str
    stats_text_color: str
    disable_flag: str
    hide_nickname: str
    hide_clan_tag: str
    disable_stats_blocks: str
    disable_rating_stats: str
    disable_cache_label: str


class Descr9(BaseModel):
    this: str
    sub_descr: SubDescr5


class Errors9(BaseModel):
    color_error: str
    changes_not_found: str


class Info9(BaseModel):
    set_ok: str
    preview: str


class Items1(BaseModel):
    color_error_note: str
    color_error_footer: str


class ImageSettings(BaseModel):
    descr: Descr9
    errors: Errors9
    info: Info9
    items: Items1


class SubDescr6(BaseModel):
    allow_custom_backgrounds: str


class Descr10(BaseModel):
    this: str
    sub_descr: SubDescr6


class Errors10(BaseModel):
    permission_denied: str


class Info10(BaseModel):
    set_ok: str


class ServerSettings(BaseModel):
    descr: Descr10
    errors: Errors10
    info: Info10
    items: str


class Descr11(BaseModel):
    this: str
    sub_descr: str


class Info11(BaseModel):
    get_ok: str


class Items2(BaseModel):
    use_custom_bg: str
    glass_effect: str
    blocks_bg_opacity: str
    nickname_color: str
    clan_tag_color: str
    stats_color: str
    main_text_color: str
    stats_text_color: str
    negative_stats_color: str
    positive_stats_color: str
    disable_flag: str
    hide_nickname: str
    hide_clan_tag: str
    disable_stats_blocks: str
    disable_rating_stats: str
    disable_cache_label: str
    stats_blocks_disabled: str


class ImageSettingsGet(BaseModel):
    descr: Descr11
    errors: str
    info: Info11
    items: Items2


class Items3(BaseModel):
    settings_list: str


class ServerSettingsGet(BaseModel):
    descr: Descr11
    errors: str
    info: Info11
    items: Items3


class Info13(BaseModel):
    reset_ok: str


class ServerSettingsReset(BaseModel):
    descr: Descr11
    errors: str
    info: Info13
    items: str


class ImageSettingsReset(BaseModel):
    descr: Descr11
    errors: str
    info: Info13
    items: str


class SubDescr7(BaseModel):
    server: str


class Descr15(BaseModel):
    this: str
    sub_descr: SubDescr7


class Info15(BaseModel):
    unset_background_ok: str


class ResetBackground(BaseModel):
    descr: Descr15
    errors: Errors10
    info: Info15
    items: str


class Descr16(BaseModel):
    this: str
    sub_descr: str


class Info16(BaseModel):
    send_ok: str
    send_ok_dm: str


class Items4(BaseModel):
    help: str


class Help(BaseModel):
    descr: Descr16
    errors: str
    info: Info16
    items: Items4


class SubDescr8(BaseModel):
    file: str


class Descr17(BaseModel):
    this: str
    sub_descr: SubDescr8


class Errors12(BaseModel):
    parsing_error: str
    uncorrect_file_format: str


class Common1(BaseModel):
    win: str
    lose: str
    draw: str


class Items5(BaseModel):
    avg_stats: str
    empty_player: str
    title: str
    common: Common1
    description: str


class ParseReplay(BaseModel):
    descr: Descr17
    errors: Errors12
    info: str
    items: Items5


class Descr18(BaseModel):
    this: str


class Info17(BaseModel):
    cooldown_not_expired: str


class Cooldown(BaseModel):
    descr: Descr18
    info: Info17


class Cmds(BaseModel):
    astats: Astats
    stats: Stats
    set_player: SetPlayer
    set_lang: SetLang
    session_state: SessionState
    get_session: GetSession
    start_session: StartSession
    start_autosession: StartAutosession
    set_background: SetBackground
    image_settings: ImageSettings
    server_settings: ServerSettings
    image_settings_get: ImageSettingsGet
    server_settings_get: ServerSettingsGet
    server_settings_reset: ServerSettingsReset
    image_settings_reset: ImageSettingsReset
    reset_background: ResetBackground
    help: Help
    parse_replay: ParseReplay
    cooldown: Cooldown


class Localization(BaseModel):
    for_image: ForImage
    map_names: MapNames
    gamemodes: Gamemodes
    frequent: Frequent
    cmds: Cmds
