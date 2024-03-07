from PIL import ImageFont


class Fonts():
    """Class that defines different fonts used in the application."""
    roboto_40 = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=40)
    """The Roboto font with a size of 40."""

    roboto = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=28)
    """The Roboto font with a size of 28."""

    roboto_small = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=18)
    """The Roboto font with a smaller size of 18."""
    
    roboto_medium = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=20)
    """The Roboto font with a size of 20."""

    roboto_small2 = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=15)
    """The Roboto font with an even smaller size of 15."""
    
    roboto_icons = ImageFont.truetype('res/fonts/Roboto-icons.ttf', size=25)
    """The Roboto font with a size of 25."""
    
    anca_coder = ImageFont.truetype('res/fonts/Anca-Coder_bold.ttf', size=18)
    """The Anca Coder font with a size of 22."""
    
    roboto_25 = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=25)
    """The Roboto font with a size of 25."""

    point = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=100)
    """The Roboto font with a large size of 100."""