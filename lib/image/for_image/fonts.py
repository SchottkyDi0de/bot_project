from PIL import ImageFont


class Fonts():
    """Class that defines different fonts used in the application."""
    roboto_22 = ImageFont.truetype('res/fonts/OFL-Licensed/RobotoCondensed-Black-mod.ttf', size=22)
    """The Roboto font with a size of 20."""
    
    anca_coder = ImageFont.truetype('res/fonts/Anca-Coder_bold.ttf', size=18)
    """The Anca Coder font with a size of 18."""
    
    anca_coder_16 = anca_coder.font_variant(size=16)
    """The Anca Coder font with a size of 16."""
    
    roboto_25 = roboto_22.font_variant(size=25)
    """The Roboto font with a size of 25."""

    roboto_40 = roboto_22.font_variant(size=40)
    """The Roboto font with a size of 40."""

    roboto_30 = roboto_22.font_variant(size=30)
    """The Roboto font with a size of 28."""

    roboto_20 = roboto_22.font_variant(size=20)
    """The Roboto font with a smaller size of 18."""

    roboto_17 = roboto_22.font_variant(size=17)
    """The Roboto font with an even smaller size of 15."""
    
    roboto_27 = roboto_22.font_variant(size=27)
    """The Roboto font with a size of 25."""

    roboto_100 = roboto_22.font_variant(size=100)
    """The Roboto font with a large size of 100."""