from discord import Colour
from discord import Embed

from lib.utils.singleton_factory import singleton
from lib.locale.locale import Text

@singleton
class InfoMSG:

    def player_not_registred(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=Text().get().frequent.info.player_not_registred,
            colour=Colour.orange()
        )

    def set_player_ok(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=Text().get().cmds.set_player.info.set_player_ok,
            colour=Colour.green()
        )

    def player_not_registred_session(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=Text().get().cmds.start_session.info.player_not_registred,
            colour=Colour.orange()
        )
    
    def player_not_registred_astats(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=Text().get().cmds.astats.info.player_not_registred,
            colour=Colour.orange()
        )

    def session_started(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=Text().get().cmds.start_session.info.started,
            colour=Colour.green()
        )

    def set_lang_ok(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=Text().get().cmds.set_lang.info.set_lang_ok,
            color=Colour.green()
        )

    def help_syntax(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=Text().get().cmds.help.items.syntax,
            colour=Colour.blurple()
        )

    def help_setup(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=Text().get().cmds.help.items.setup,
            colour=Colour.blurple()
        )

    def help_statistics(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=Text().get().cmds.help.items.statistics,
            colour=Colour.blurple()
        )

    def help_session(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=Text().get().cmds.help.items.session,
            colour=Colour.blurple()
        )
    def help_other(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=Text().get().cmds.help.items.other,
            colour=Colour.blurple()
        )

    def help_send_ok(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=Text().get().cmds.help.info.send_ok,
            colour=Colour.green()
        )
    def session_state(self, text: str) -> Embed:
        return Embed(
            title=Text().get().frequent.info.info,
            description=text,
            colour=Colour.green()
        )
    
    def cooldown_not_expired(self) -> Embed:
        return Embed(
            title=self.text_obj.get().frequent.info.warning,
            description=self.text_obj.get().cmds.cooldown.info.cooldown_not_expired,
            color=Colour.red()
        )
    
    def custom(
            self,
            text: str,
            title: str = Text().get().frequent.info.info,
            colour: str = 'blurple'
        ) -> Embed:
    
        colour = getattr(Colour, colour)
        return Embed(
            title=title,
            description=text,
            colour=colour()
        )
        