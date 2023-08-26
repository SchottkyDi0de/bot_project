from discord import Colour, Embed

from lib.locale.locale import Text


class ErrorMSG():
    text = Text()
    api_error = Embed(
        title=text.data.errors.error,
        description=text.data.errors.api_error,
        colour=Colour.red()
    )
    player_not_found = Embed(
        title=text.data.errors.error,
        description=text.data.errors.player_not_found,
        colour=Colour.red()
    )
    need_more_battles = Embed(
        title=text.data.errors.error,
        description=text.data.errors.no_battles,
        colour=Colour.red()
    )
    unknown_error = Embed(
        title=text.data.errors.error,
        description=text.data.errors.unknown_error,
        colour=Colour.red()
    )
    uncorrect_region = Embed(
        title=text.data.errors.error,
        description=text.data.errors.incorrect_region,
        colour=Colour.red()
    )
    uncorrect_name = Embed(
        title=text.data.errors.error,
        description=text.data.errors.incorrect_name,
        color=Colour.red()
    )
    parser_error = Embed(
        title=text.data.errors.error,
        description=text.data.errors.parser_error,
        colour=Colour.red()
    )
    session_not_found = Embed(
        title=text.data.errors.error,
        description=text.data.errors.session_not_found,
        colour=Colour.red()
    )
    session_not_updated = Embed(
        title=text.data.errors.error,
        description=text.data.errors.session_not_updated,
        colour=Colour.red()
    )
