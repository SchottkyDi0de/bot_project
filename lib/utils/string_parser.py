from typing import Any

def insert_data(string: str, key_values: dict[str, str]) -> str:
    """
    Replaces placeholders in a string with corresponding values.

    Args:
        string (str): The input string containing placeholders.
        key_values (dict[str, str]): A dictionary mapping placeholder names to their corresponding values.

    Returns:
        str: The updated string with placeholders replaced by values.

    Example:
        insert_data("My name is <name>, {"name" : "Josh"})
        >>> "My name is Josh"
    """

    for _, (key, value) in enumerate(key_values.items()):
        string = string.replace(f'<{key}>', value, 1)
    return string
