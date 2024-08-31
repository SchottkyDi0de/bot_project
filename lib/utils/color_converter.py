from lib.image.utils.color_validator import color_validate
from webcolors import hex_to_rgb

def get_tuple_from_color(color: str | None) -> tuple[int, int, int] | bool:
    """
    Converts a color string to a tuple of RGB values.

    Args:
        color (str | None): The color string to convert. It can be in either hexadecimal or RGB format.

    Returns:
        tuple[int, int, int] | bool: A tuple of RGB values if the color string is valid, otherwise False.
    """
    
    validate = color_validate(color)
    if validate is not None:
        if validate[1] == 'hex':
            return hex_to_rgb(color)
        if validate[1] == 'rgb':
            return (int(i) for i in validate[0].groups())
    else:
        return False