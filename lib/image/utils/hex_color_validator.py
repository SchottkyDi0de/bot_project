import re


def hex_color_validate(color: str | None) -> bool:
    if color is None:
        return False
    
    return re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color) is not None