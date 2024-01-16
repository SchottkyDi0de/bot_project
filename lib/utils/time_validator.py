import re

def validate(time_str: str) -> bool:
    regex = r'^[0-9]{2}:[0-9]{2}:[0-9]{2}$'
    return re.match(regex, time_str) is not None