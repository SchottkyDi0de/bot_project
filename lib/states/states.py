from aiogram.fsm.state import State, StatesGroup


class SetPlayerStates(StatesGroup):
    set_nick = State()


class AutoSessionStates(StatesGroup):
    set_restart_time = State()
    set_timezone = State()


class ImageSettingsStates(StatesGroup):
    custom_bg = State()
    change_color = State()
    glass_effect = State()
    blocks_bg_brightness = State()


class SessionWidgetStates(StatesGroup):
    io = State()


class HookStates(StatesGroup):
    target_nickname = State()
    target_value = State()

class ReplayStates(StatesGroup):
    gf = State()
