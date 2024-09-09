from lib.data_classes.db_player import BadgesEnum


def validate_badge(badge: str) -> BadgesEnum | None:
    """
    Validate the given badge by checking if it exists in the BadgesEnum.
    
    Parameters:
        badge (str): The badge to validate.
    
    Returns:
        BadgesEnum | None: The validated badge if it exists, None otherwise.
    """
    if badge in BadgesEnum.__members__.keys():
        return BadgesEnum[badge]
    else:
        return None
    
def sort_badges(badges: list[str], reverse: bool = True) -> list[str]:
    """
    Sort the given list of badges by their order in the BadgesEnum.
    
    Parameters:
        badges (list[str]): The list of badges to sort.
    
    Returns:
        list[str]: The sorted list of badges.
    """
    return sorted(badges, key=lambda badge: BadgesEnum[badge].value, reverse=reverse)