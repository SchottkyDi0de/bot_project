from discord import Colour, Embed

from lib.locale.locale import Text


class ErrorMSG():
    text = Text().get()

    api_error = Embed(
        title=text.errors.error,
        description=text.errors.api_error,
        colour=Colour.red()
    )
    player_not_found = Embed(
        title=text.errors.error,
        description=text.errors.player_not_found,
        colour=Colour.red()
    )
    need_more_battles = Embed(
        title=text.errors.error,
        description=text.errors.no_battles,
        colour=Colour.red()
    )
    unknown_error = Embed(
        title=text.errors.error,
        description=text.errors.unknown_error,
        colour=Colour.red()
    )
    uncorrect_region = Embed(
        title=text.errors.error,
        description=text.errors.incorrect_region,
        colour=Colour.red()
    )
    uncorrect_name = Embed(
        title=text.errors.error,
        description=text.errors.incorrect_name,
        color=Colour.red()
    )
    parser_error = Embed(
        title=text.errors.error,
        description=text.errors.parser_error,
        colour=Colour.red()
    )
    session_not_found = Embed(
        title=text.errors.error,
        description=text.errors.session_not_found,
        colour=Colour.red()
    )
    session_not_updated = Embed(
        title=text.errors.error,
        description=text.errors.session_not_updated,
        colour=Colour.red()
    )
    def update_locale(self):
        self.text = Text().get()
