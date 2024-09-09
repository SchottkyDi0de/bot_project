from .session_widget import *


def get_validator_by_name(name: str, return_object: bool=False) -> Validator:
    name = name.replace("_", " ").title().replace(" ", "")
    cls = globals()[name]
    if return_object:
        return cls()
    return cls
