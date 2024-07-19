from lib.data_classes.db_player import AccountSlotsEnum, GameAccount
from lib.data_classes.locale_struct import Localization
from lib.utils.string_parser import insert_data


def get_formatted_slot_info(slot: AccountSlotsEnum, text: Localization, game_account: GameAccount, shorted: bool = False, clear_md: bool = False) -> str:
    """
    Get formatted slot information.

    Args:
        slot (AccountSlotsEnum): The slot to get information for.
        text (Localization): The localization object.
        game_account (GameAccount): The game account object.
        shorted (bool, optional): Whether to use the short slot info. Defaults to False.
        clear_md (bool, optional): Whether to clear markdown. Defaults to False.

    Returns:
        str: The formatted slot information.
    """
    if not isinstance(slot, AccountSlotsEnum):
        raise TypeError(f'slot must be an instance of AccountSlotsEnum, not {slot.__class__.__name__}')

    data = insert_data(
        text.frequent.info.slot_info if not shorted else text.frequent.info.short_slot_info,
        {
            'slot_num' : slot.value,
            'nickname' : game_account.nickname,
            'region' : game_account.region.upper(),
        },
        clear_md=clear_md
    )
    return data