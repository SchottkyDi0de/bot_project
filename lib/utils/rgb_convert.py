from lib.image.utils.color_validator import CompiledRegex


def rgb_convert(rgb: str | None):
    if not rgb:
        return
    
    return '#' + ''.join(f'{int(i):02x}' for i in CompiledRegex.rgb.match(rgb).groups())