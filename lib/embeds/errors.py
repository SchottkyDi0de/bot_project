from discord import Colour, Embed

from lib.utils.singleton_factory import singleton
from lib.locale.locale import Text


@singleton
class ErrorMSG:
    text_obj = Text()

    def api_error(self) -> Embed:
        return Embed(
            title=self.text_obj.get().frequent.errors.error,
            description=self.text_obj.get().frequent.errors.api_error,
            colour=Colour.red()
        ).set_footer(text=self.text_obj.get().frequent.info.err_info_sent)
    
    def player_not_found(self) -> Embed:
        return Embed(
            title=self.text_obj.get().frequent.errors.error,
            description=self.text_obj.get().cmds.stats.errors.player_not_found,
            colour=Colour.red()
        )
    
    def need_more_battles(self) -> Embed: 
        return Embed(
            title=self.text_obj.get().frequent.errors.error,
            description=self.text_obj.get().cmds.stats.errors.no_battles,
            colour=Colour.red()
        )
    
    def unknown_error(self) -> Embed:
        return Embed(
            title=self.text_obj.get().frequent.errors.error,
            description=self.text_obj.get().frequent.errors.unknown_error,
            colour=Colour.red()
        ).set_footer(text=self.text_obj.get().frequent.info.err_info_sent)
    
    def uncorrect_name(self) -> Embed:
        return Embed(
            title=self.text_obj.get().frequent.errors.error,
            description=self.text_obj.get().cmds.stats.errors.uncorrect_nickname,
            color=Colour.red()
        )
    
    def parser_error(self) -> Embed:
        return Embed(
            title=self.text_obj.get().frequent.errors.error,
            description=self.text_obj.get().frequent.errors.parser_error,
            colour=Colour.red()
        ).set_footer(text=self.text_obj.get().frequent.info.err_info_sent)
    
    def session_not_found(self) -> Embed:
        return Embed(
            title=self.text_obj.get().frequent.errors.error,
            description=self.text_obj.get().cmds.get_session.errors.session_not_found,
            colour=Colour.red()
        )
    
    def session_not_updated(self) -> Embed:
        return Embed(
            title=self.text_obj.get().frequent.errors.error,
            description=self.text_obj.get().cmds.get_session.errors.session_not_updated,
            colour=Colour.red()
        )
    
    def user_banned(self) -> Embed:
        return Embed(
            title=self.text_obj.get().frequent.errors.error,
            description=self.text_obj.get().frequent.errors.user_banned,
            colour=Colour.red()
        )
    
    def set_lang_perm(self) -> Embed:
        return Embed(
            title=self.text_obj.get().frequent.errors.error,
            description=self.text_obj.get().cmds.set_lang.errors.permission_denied,
            colour=Colour.red()
        )
    
    def set_lang_unregistred(self) -> Embed:
        return Embed(
            title=self.text_obj.get().frequent.errors.error,
            description=self.text_obj.get().cmds.set_lang.errors.player_not_registred,
            colour=Colour.red()
        )
    
    def cooldown_not_expired(self) -> Embed:
        return Embed(
            title=self.text_obj.get().frequent.errors.error,
            description=self.text_obj.get().cmds.cooldown.errors.cooldown_not_expired,
            color=Colour.red()
        )

    def custom(
            self, 
            text: str,
            title: str = text_obj.get().frequent.errors.error,
            colour: str = 'red',
            err_inf_sent: bool = False
            ) -> Embed:
        embed =  Embed(
            title=title,
            description=text,
            colour=getattr(Colour, colour)()
        )
        if err_inf_sent:
            embed.set_footer(text=self.text_obj.get().frequent.info.err_info_sent)
            
        return embed
    