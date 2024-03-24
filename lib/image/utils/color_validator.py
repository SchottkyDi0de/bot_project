from re import compile as _compile, Match
from typing import Callable, Literal


class CompiledRegex:
    hex = _compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')
    rgb = _compile(r'^[(]?(\d{,3})\W+(\d{,3})\W+(\d{,3})[)]?$')


class ColorValidators:
    @staticmethod
    def get_validator(type: str) -> Callable[[str | None], Match | None]:
        return getattr(ColorValidators, f"{type}_color_validate")
    
    @staticmethod
    def hex_color_validate(color: str | None) -> Match | None:
        return CompiledRegex.hex.match(color)
    
    @staticmethod
    def rgb_color_validate(color: str | None) -> Match | None:
        return CompiledRegex.rgb.match(color)


def color_validate(color: str | None) -> tuple[Match, Literal['hex', 'rgb']] | None:
    if color is None:
        return False
    
    match_hex = ColorValidators.hex_color_validate(color)
    if match_hex is not None:
        return match_hex, 'hex'
        
    match_rgb = ColorValidators.rgb_color_validate(color)
    if match_rgb is not None:
        return match_rgb, 'rgb'
        
    return None