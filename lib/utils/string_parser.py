def insert_data(string: str, key_values: dict[str, str]) -> str:
    """
    Replaces placeholders in a string with corresponding values.
    
    Args:
        string (str): The input string containing placeholders.
        key_values (dict[str, str]): A dictionary mapping placeholder names to their corresponding values.
        clear_md (bool, optional): Whether to remove Markdown formatting from the resulting string. Defaults to False.
    
    Returns:
        str: The updated string with placeholders replaced by values.
    
    Usage Example:
        >>> string = "Hello, <name>! Welcome to <event>."
        >>> key_values = {
        ...     "name": "John",
        ...     "event": "party"
        ... }
        >>> result = insert_data(string, key_values)
        >>> print(result)
        Hello, John! Welcome to party.
    """
    for key, value in key_values.items():
        string = string.replace(f'<{key}>', str(value), 1)
    
    return string
