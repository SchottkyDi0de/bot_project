from discord import Colour, Embed

from lib.utils.singleton_factory import singleton
from lib.locale.locale import Text


@singleton
class ErrorMSG:

    def api_error(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().frequent.errors.api_error,
            colour=Colour.red()
        )
    
    def player_not_found(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().cmds.stats.errors.player_not_found,
            colour=Colour.red()
        )
    
    def need_more_battles(self) -> Embed: 
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().cmds.stats.errors.no_battles,
            colour=Colour.red()
        )
    
    def unknown_error(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().frequent.errors.unknown_error,
            colour=Colour.red()
        )
    
    def uncorrect_name(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().cmds.stats.errors.uncorrect_nickanme,
            color=Colour.red()
        )
    
    def parser_error(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().frequent.errors.parser_error,
            colour=Colour.red()
        )
    
    def session_not_found(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().cmds.get_session.errors.session_not_found,
            colour=Colour.red()
        )
    
    def session_not_updated(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().cmds.get_session.errors.session_not_updated,
            colour=Colour.red()
        )
    
    def user_banned(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().frequent.errors.user_banned,
            colour=Colour.red()
        )
    
    def set_lang_perm(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().cmds.set_lang.errors.permission_denied,
            colour=Colour.red()
        )
    
    def set_lang_unregistred(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().cmds.set_lang.errors.player_not_registred,
            colour=Colour.red()
        )
    def custom(self, text: str) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=text,
            colour=Colour.red()
        )
    