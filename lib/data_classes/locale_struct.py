from pydantic import BaseModel, Field


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
    frags_per_battle: str
    max_frags: str
    enemies_destroyed: str
    destruction_ratio: str
    damage_dealt: str
    damage_ratio: str
    avg_spotted: str
    survived_battles: str
    xp: str
    max_xp: str
    shots: str
    accuracy: str
    no_clan: str
    no_data: str
    survival_ratio: str
    dropped_capture_points: str
    capture_points: str
    damage_received: str
    leaderboard_position: str
    hits: str
    frags: str
    losses: str
    wins: str


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
    yukon: str
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


class Info(BaseModel):
    unregistred_player: str
    is_channel: str
    try_again: str
    good_button_respoce: str
    premium_only: str
    info: str
    err_info_sent: str
    warning: str
    discard_changes: str
    session_already_started: str


class Errors(BaseModel):
    error: str
    missing_argument: str
    too_many_arguments: str
    invalid_argument: str
    bad_button_responce: str
    wrong_file_type: str
    cooldown: str
    unknown_error: str
    user_banned: str
    api_error: str
    parser_error: str


class Frequent(BaseModel):
    common: Common
    info: Info
    errors: Errors


class Start(BaseModel):
    descr: str


class Help(BaseModel):
    descr: str


class SubDescr(BaseModel):
    get_nickname: str
    get_region: str


class Info1(BaseModel):
    invalid_nickname: str
    choosed_region: str
    set_player_ok: str
    choose_slot: str


class SetPlayer(BaseModel):
    descr: str
    sub_descr: SubDescr
    info: Info1


class Errors1(BaseModel):
    player_not_found: str
    uncorrect_nickname: str
    no_battles: str


class Stats(BaseModel):
    errors: Errors1


class Info2(BaseModel):
    set_lang_ok: str


class SubDescr1(BaseModel):
    choose_lang: str


class SetLang(BaseModel):
    descr: str
    info: Info2
    sub_descr: SubDescr1


class Errors2(BaseModel):
    session_not_found: str


class Items(BaseModel):
    started: str
    started_part2: str
    not_started: str


class SessionState(BaseModel):
    errors: Errors2
    items: Items


class Info3(BaseModel):
    started: str


class StartSession(BaseModel):
    info: Info3


class SubDescr2(BaseModel):
    get_timezone: str
    get_restart_time: str


class Errors3(BaseModel):
    uncorrect_tz: str
    uncorrect_r_time: str


class StartAutosession(BaseModel):
    info: Info3
    sub_descr: SubDescr2
    errors: Errors3


class Errors4(BaseModel):
    session_not_found: str


class GetSession(BaseModel):
    errors: Errors4


class Buttons4(BaseModel):
    start_session: str
    stop_session: str
    get_session: str
    autosession: str
    timezone: str
    restart_time: str
    back: str


class SubDescr8(BaseModel):
    ss_main_text: str
    success_started: str
    success_stopped: str
    buttons: Buttons4


class Session(BaseModel):
    descr: str
    sub_descr: SubDescr8


class SubDescr3(BaseModel):
    use_custom_bg: str
    colorize_stats: str
    glass_effect: str
    stats_blocks_transparency: str
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


class Descr(BaseModel):
    this: str
    sub_descr: SubDescr3


class Info5(BaseModel):
    set_ok: str


class SubDescr4(BaseModel):
    set_bg: str
    main_text: str
    preview: str
    choose_color2change: str
    type_new_color: str
    choose_param2change: str
    glass_effect: str
    reset_bg: str
    available_themes: str


class Background(BaseModel):
    oversize: str
    small_resolution: str


class MainButtons(BaseModel):
    bg: str
    theme: str
    colors: str
    other: str
    reset: str
    save: str
    back: str


class ColorsButtons(BaseModel):
    nickname_color: str
    clan_tag_color: str
    stats_color: str
    main_text_color: str
    stats_text_color: str
    negative_stats_color: str
    positive_stats_color: str


class OthersButtons(BaseModel):
    use_custom_bg: str
    colorize_stats: str
    disable_flag: str
    hide_nickname: str
    hide_clan_tag: str
    disable_stats_blocks: str
    disable_rating_stats: str
    disable_cache_label: str
    glass_effect: str
    blocks_bg_brightness: str
    on_: str
    off_: str


class Items1(BaseModel):
    color_error_footer: str
    background: Background
    main_buttons: MainButtons
    colors_buttons: ColorsButtons
    others_buttons: OthersButtons


class Descr1(BaseModel):
    this: str
    sub_descr: str


class Info6(BaseModel):
    get_ok: str


class Items2(BaseModel):
    theme: str
    use_custom_bg: str
    colorize_stats: str
    glass_effect: str
    stats_blocks_transparency: str
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


class SettingsRepresentAlias(BaseModel):
    descr: Descr1
    errors: str
    info: Info6
    items: Items2


class ImageSettings(BaseModel):
    descr: Descr
    info: Info5
    sub_descr: SubDescr4
    items: Items1
    settings_represent_alias: SettingsRepresentAlias


class Descr2(BaseModel):
    mtext: str
    success: str


class SubDescr5(BaseModel):
    main_button: str
    preview_text: str
    save: str


class StatsViewSettings(BaseModel):
    descr: Descr2
    sub_descr: SubDescr5


class Descr3(BaseModel):
    this: str


class Info7(BaseModel):
    success: str


class Edit(BaseModel):
    descr: str
    io_change: str
    io_success: str
    success_onoff: str
    bool_change: str


class EditButtons(BaseModel):
    max_stats_blocks: str
    max_stats_small_blocks: str
    background_transparency: str
    adaptive_width: str
    stats_block_color: str
    disable_main_stats_block: str
    use_bg_for_stats_blocks: str
    disable_nickname: str
    disable_bg: str
    update_time: str


class Buttons(BaseModel):
    field_on: str = Field(..., alias='_on')
    field_off: str = Field(..., alias='_off')
    edit: str
    reset: str
    save: str
    back: str
    edit_buttons: EditButtons


class Settings(BaseModel):
    descr: str
    info: Info7
    edit: Edit
    buttons: Buttons


class SessionWidget(BaseModel):
    descr: Descr3
    info: Info7
    settings: Settings


class Buttons1(BaseModel):
    profile: str
    image: str
    session_widget: str


class SessionWidget1(BaseModel):
    stats_block_color: str


class Validators(BaseModel):
    session_widget: SessionWidget1


class SubDescr6(BaseModel):
    main_text: str
    buttons: Buttons1
    validators: Validators
    profile_text: str
    profile_switch_success: str


class Settings1(BaseModel):
    descr: str
    sub_descr: SubDescr6


class Info9(BaseModel):
    active_descr: str
    choose_target_stats: str
    activated: str
    hook_ended: str
    disabled: str


class SubDescr7(BaseModel):
    type_nickname: str
    choose_trigger: str
    type_value: str
    choose_target_region: str
    watch_for: str
    hook_state: str


class Buttons2(BaseModel):
    new_hook: str
    hook_state: str
    disable_hook: str
    main: str
    sess: str
    diff: str


class Hook(BaseModel):
    info: Info9
    sub_descr: SubDescr7
    buttons: Buttons2


class Errors5(BaseModel):
    parsing_error: str


class Buttons3(BaseModel):
    main_back: str
    back: str


class Common1(BaseModel):
    win: str
    lose: str
    draw: str


class Items4(BaseModel):
    description: str
    formenu: str
    avg_stats: str
    empty_player: str
    title: str
    common: Common1
    buttons: Buttons3


class Info10(BaseModel):
    send_file: str
    choose_region: str


class ParseReplay(BaseModel):
    info: Info10
    items: Items4
    errors: Errors5


class Items3(BaseModel):
    profile: str
    level: str
    exp: str
    last_commands: str
    last_activity: str
    commands_counter: str
    accounts_info: str
    badges: str
    command_name: str
    last_used_time: str
    num: str
    account: str
    session: str
    others: str
    premium: str
    premium_time: str


class Profile(BaseModel):
    descr: Descr3
    items: Items3


class Cmds(BaseModel):
    start: Start
    help: Help
    set_player: SetPlayer
    stats: Stats
    set_lang: SetLang
    session_state: SessionState
    start_session: StartSession
    start_autosession: StartAutosession
    get_session: GetSession
    session: Session
    image_settings: ImageSettings
    stats_view_settings: StatsViewSettings
    session_widget: SessionWidget
    settings: Settings1
    hook: Hook
    parse_replay: ParseReplay
    profile: Profile


class Localization(BaseModel):
    for_image: ForImage
    map_names: MapNames
    gamemodes: Gamemodes
    frequent: Frequent
    cmds: Cmds
