from discord import Colour
from discord import Embed
from lib.locale import locale


class InfoMSG():
    text = locale.Text()
    player_not_registred = Embed(
        title=text.data.info.info,
        description=text.data.info.player_not_registred,
        colour=Colour.orange()
    )
    set_player_ok = Embed(
        title=text.data.info.info,
        description=text.data.info.set_player_ok,
        colour=Colour.green()
    )
    player_not_registred_session = Embed(
        title=text.data.info.info,
        description=text.data.info.player_not_registred_session,
        colour=Colour.orange()
    )
    session_started = Embed(
        title=text.data.info.info,
        description=text.data.info.session_started,
        colour=Colour.green()
    )
