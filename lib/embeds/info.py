from discord import Colour
from discord import Embed
from lib.locale.locale import Text


class InfoMSG():
    def __init__(self):
        text = Text().get()

        self.player_not_registred = Embed(
            title=text.info.info,
            description=text.info.player_not_registred,
            colour=Colour.orange()
        )
        self.set_player_ok = Embed(
            title=text.info.info,
            description=text.info.set_player_ok,
            colour=Colour.green()
        )
        self.player_not_registred_session = Embed(
            title=text.info.info,
            description=text.info.player_not_registred_session,
            colour=Colour.orange()
        )
        self.session_started = Embed(
            title=text.info.info,
            description=text.info.session_started,
            colour=Colour.green()
        )
        self.set_lang_ok = Embed(
            title=text.info.info,
            description=text.info.set_lang_ok,
            color=Colour.green()
        )
        self.help_syntax = Embed(
            title=text.info.info,
            description=text.help.syntax,
            colour=Colour.blurple()
        )
        self.help_setup = Embed(
            title=text.info.info,
            description=text.help.setup,
            colour=Colour.blurple()
        )
        self.help_statistics = Embed(
            title=text.info.info,
            description=text.help.statistics,
            colour=Colour.blurple()
        )
        self.help_session = Embed(
            title=text.info.info,
            description=text.help.session,
            colour=Colour.blurple()
        )
        self.help_send_ok = Embed(
            title=text.info.info,
            description=text.help.send_ok,
            colour=Colour.green()
        )
