from discord import Colour, Embed

from lib.utils.singleton_factory import singleton
from lib.locale.locale import Text
from lib.data_classes.locale_struct import Localization


@singleton
class ErrorMSG:

    def api_error(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().frequent.errors.api_error,
            colour=Colour.red()
        ).set_footer(text=Text().get().frequent.info.err_info_sent)
    
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
        ).set_footer(text=Text().get().frequent.info.err_info_sent)
    
    def uncorrect_name(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().cmds.stats.errors.uncorrect_nickname,
            color=Colour.red()
        )
    
    def parser_error(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().frequent.errors.parser_error,
            colour=Colour.red()
        ).set_footer(text=Text().get().frequent.info.err_info_sent)
    
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
    
    def set_lang_unregistered(self) -> Embed:
        return Embed(
            title=Text().get().frequent.errors.error,
            description=Text().get().cmds.set_lang.errors.player_not_registred,
            colour=Colour.red()
        )

    def custom(
            self,
            locale: Localization,
            text: str,
            title: str = None,
            colour: str = 'red',
            err_inf_sent: bool = False
            ) -> Embed:
        embed =  Embed(
            title=title if title is not None else locale.frequent.errors.error,
            description=text,
            colour=getattr(Colour, colour)()
        )
        if err_inf_sent:
            embed.set_footer(text=Text().get().frequent.info.err_info_sent)
            
        return embed
    