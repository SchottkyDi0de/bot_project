from lib.locale.locale import Text


def bool_handler(data: bool) -> str:
    """
    Returns a string representation of a boolean value.

    Args:
        data (bool): The boolean value to be converted.

    Returns:
        str: The string representation of the boolean value.
    """
    if data:
        return Text().get().frequent.common.yes
    else:
        return Text().get().frequent.common.no