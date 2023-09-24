from discord import Colour, Embed

from lib.locale.locale import Text


class ErrorMSG():
    def __init__(self):
        text = Text().get()

        self.api_error = Embed(
            title=text.errors.error,
            description=text.errors.api_error,
            colour=Colour.red()
        )
        self.player_not_found = Embed(
            title=text.errors.error,
            description=text.errors.player_not_found,
            colour=Colour.red()
        )
        self.need_more_battles = Embed(
            title=text.errors.error,
            description=text.errors.no_battles,
            colour=Colour.red()
        )
        self.unknown_error = Embed(
            title=text.errors.error,
            description=text.errors.unknown_error,
            colour=Colour.red()
        )
        self.uncorrect_region = Embed(
            title=text.errors.error,
            description=text.errors.incorrect_region,
            colour=Colour.red()
        )
        self.uncorrect_name = Embed(
            title=text.errors.error,
            description=text.errors.incorrect_name,
            color=Colour.red()
        )
        self.parser_error = Embed(
            title=text.errors.error,
            description=text.errors.parser_error,
            colour=Colour.red()
        )
        self.session_not_found = Embed(
            title=text.errors.error,
            description=text.errors.session_not_found,
            colour=Colour.red()
        )
        self.session_not_updated = Embed(
            title=text.errors.error,
            description=text.errors.session_not_updated,
            colour=Colour.red()
        )
        self.user_banned = Embed(
            title=text.errors.error,
            description=text.errors.user_banned,
            colour=Colour.red()
        )