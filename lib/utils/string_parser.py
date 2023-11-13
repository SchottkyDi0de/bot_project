def insert_data(string: str, keys: tuple[str], values: tuple[str]) -> str:
    """
    Replaces placeholders in a string with corresponding values.

    Args:
        string (str): The input string containing placeholders.
        keys (tuple[str]): The keys representing the placeholders.
        values (tuple[str]): The values to replace the placeholders.

    Returns:
        str: The updated string with placeholders replaced by values.

    Example:
        insert_data("My name is <name>, ("name", ), ("Josh", ))
        >>> "My name is Josh"
    """

    for index, key in enumerate(keys):
        string = string.replace(f'<{key}>', values[index], 1)
    return string
