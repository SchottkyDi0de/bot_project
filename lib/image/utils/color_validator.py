from re import compile as _compile
from typing import Literal


class CompiledRegex:
    hex = _compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')
    rgb = _compile(r'^[(]?(\d{,3})\W+(\d{,3})\W+(\d{,3})[)]?$')


class ColorValidators:
    def get_validator(type: str):
        return getattr(ColorValidators, f"{type}_color_validate")
    
    def hex_color_validate(color: str | None) -> bool:
        if color is None:
            return False
    
        return CompiledRegex.hex.match(color) is not None
    
    def rgb_color_validate(color: str | None) -> bool:
        if color is None:
            return False

        re = CompiledRegex.rgb.match(color)
        if not re:
            return False
        
        return all(0 <= int(i) <= 255 for i in re.groups())


def color_validate(color: str | None) -> tuple[bool, Literal['hex', 'rgb']]:
    if color is None:
        return False, 'hex'
    
    if ColorValidators.hex_color_validate(color):
        return True, 'hex'

    return ColorValidators.rgb_color_validate(color), 'rgb'