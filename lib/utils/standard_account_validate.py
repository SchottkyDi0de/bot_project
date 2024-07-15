from discord import Option, SlashCommandOptionType
from lib.data_classes.db_player import AccountSlotsEnum
from lib.database.players import PlayersDB
from lib.blacklist.blacklist import check_user
from lib.data_classes.db_player import DBPlayer, GameAccount
from lib.exceptions.database import MemberNotFound, MemberNotVerified, PremiumNotFound


async def standard_account_validate(
    account_id: str | int,
    slot: AccountSlotsEnum | int | str | None | Option,
    check_premium: bool = False, 
    check_verified: bool = False,
    check_banned: bool = True,
    allow_empty_slot: bool = False
    ) -> tuple[GameAccount, DBPlayer, AccountSlotsEnum]:
    """
    Validates a standard account based on the provided account ID, slot, and optional parameters.

    Args:
        account_id (str | int): The ID of the account.
        slot (AccountSlotsEnum | int | str | None | Option, optional): The slot of the account. Defaults to None.
        check_premium (bool, optional): Whether to check if the account has premium. Defaults to False.
        check_verified (bool, optional): Whether to check if the account is verified. Defaults to False.
        check_banned (bool, optional): Whether to check if the account is banned. Defaults to True.
        allow_empty_slot (bool, optional): Whether to allow an empty slot. Defaults to False.

    Returns:
        tuple[GameAccount, DBPlayer, AccountSlotsEnum]: A tuple containing the game account, the member, and the slot.

    Raises:
        TypeError: If the slot type is not supported.
        MemberNotFound: If the member is not found.
        PremiumNotFound: If the account does not have premium.
        MemberNotVerified: If the account is not verified.
        UserBanned: If the account is banned.

    """
    if slot is None:
        slot = await PlayersDB().get_current_game_slot(account_id)
    
    elif isinstance(slot, str):
        slot = AccountSlotsEnum[slot]
        
    elif isinstance(slot, int):
        slot = AccountSlotsEnum(slot)
    
    elif isinstance(slot, Option):
        if slot.input_type == SlashCommandOptionType.integer:
            slot = AccountSlotsEnum(slot.name)
        
        elif slot.input_type == SlashCommandOptionType.string:
            slot = AccountSlotsEnum[slot.name]
            
    elif isinstance(slot, AccountSlotsEnum):
        pass
            
    else:
        raise TypeError(f'Unsupported slot type: {slot.__class__.__name__}')
    
    member = await PlayersDB().check_member_exists(account_id, get_if_exist=True)
    slot = await PlayersDB().validate_slot(slot=slot, member=member, empty_allowed=allow_empty_slot)
    game_account: GameAccount = getattr(member.game_accounts, slot.name)
    
    if not isinstance(member, DBPlayer):
        raise MemberNotFound()
    
    if check_premium:
        premium = await PlayersDB().check_premium(member=member)
        if not premium:
            raise PremiumNotFound()
        
    if check_verified:
        verified = await PlayersDB().check_member_is_verified(slot=slot, member=member)
        if not verified:
            raise MemberNotVerified()
    
    if check_banned:
        check_user(account_id)
    
    return (game_account, member, slot)