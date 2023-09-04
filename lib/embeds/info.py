from discord import Colour
from discord import Embed
from lib.locale.locale import Text


class InfoMSG():
    text = Text().get()
    player_not_registred = Embed(
        title=text.info.info,
        description=text.info.player_not_registred,
        colour=Colour.orange()
    )
    set_player_ok = Embed(
        title=text.info.info,
        description=text.info.set_player_ok,
        colour=Colour.green()
    )
    player_not_registred_session = Embed(
        title=text.info.info,
        description=text.info.player_not_registred_session,
        colour=Colour.orange()
    )
    session_started = Embed(
        title=text.info.info,
        description=text.info.session_started,
        colour=Colour.green()
    )
    set_lang_ok = Embed(
        title=text.info.info,
        description=text.info.set_lang_ok,
        color=Colour.green()
    )
    
    def update_locale(self):
        self.text = Text().get()
