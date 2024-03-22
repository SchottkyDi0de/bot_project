from discord import Colour, Embed, File

from lib.data_classes.locale_struct import Localization
from lib.locale.locale import Text
from lib.utils.singleton_factory import singleton


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
            title=Text().get().frequent.info.warning,
            description=Text().get().cmds.cooldown.info.cooldown_not_expired,
            color=Colour.orange()
        )
        
    def member_not_verified(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.warning,
            description=Text().get().frequent.errors.verify_error,
            color=Colour.orange()
        )

    def not_button_owner(self) -> Embed:
        return Embed(
            title=Text().get().frequent.info.warning,
            description=Text().get().views.not_owner,
            color=Colour.orange()
        )
    
    def custom(
            self,
            locale: Localization,
            text: str,
            title: str = None,
            footer: str = None,
            image: File = None,
            colour: str = 'blurple'
        ) -> Embed:
    
        colour = getattr(Colour, colour)
        embed = Embed(
            title=title if title is not None else locale.frequent.info.info,
            description=text,
            colour=colour(),
        )
        
        if footer is not None:
            embed.set_footer(text=footer)
        if image is not None:
            embed.set_image(url=image)
        return embed
    
        