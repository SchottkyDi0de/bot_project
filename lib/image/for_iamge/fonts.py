from PIL import ImageFont

from lib.utils.singleton_factory import singleton


@singleton
class Fonts():
    """Class that defines different fonts used in the application."""
    roboto_40 = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=40)
    """The Roboto font with a size of 40."""

    roboto = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=28)
    """The Roboto font with a size of 28."""

    roboto_small = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=18)
    """The Roboto font with a smaller size of 18."""

    roboto_small2 = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=15)
    """The Roboto font with an even smaller size of 15."""

    point = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=100)
    """The Roboto font with a large size of 100."""
