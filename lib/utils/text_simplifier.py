from typing import Any, Mapping

from lib.utils.bool_to_text import bool_handler


def jsonify(locale, obj: Mapping[str, Any], highlight_keys: bool = True, highlight_sym: str = '`') -> str:
    text = ''
    sep = highlight_sym * highlight_keys
    for key, value in obj.items():
        ival = value if not isinstance(value, bool) else bool_handler(value)
        text += f'{sep}{getattr(locale, key)}{sep}: {ival}\n'
    
    return text
