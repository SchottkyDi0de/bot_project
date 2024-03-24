import re
from lib.image.utils.color_validator import color_validate, CompiledRegex
from PIL import ImageColor
from webcolors import hex_to_rgb

def get_tuple_from_color(color: str | None) -> tuple[int, int, int] | bool:
    validate = color_validate(color)
    if validate is not None:
        if validate[1] == 'hex':
            return hex_to_rgb(color)
        if validate[1] == 'rgb':
            return (int(i) for i in validate[0].groups())
    else:
        return False