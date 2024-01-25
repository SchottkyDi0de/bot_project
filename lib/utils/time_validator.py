import re

def validate(time_str: str) -> bool:
    regex = r'\b([01][0-9]|2[0-3]):([0-5][0-9])\b'
    return re.match(regex, time_str) is not None