from discord import AutocompleteContext, OptionChoice

from lib.database.players import PlayersDB
from lib.utils.standard_account_validate import standard_account_validate


async def account_selector(ctx: AutocompleteContext) -> list[str]:
    member_id = ctx.interaction.user.id
    member = await standard_account_validate(account_id=member_id, slot=None)
    possible_accounts = await PlayersDB().get_all_used_slots(member=member)
    
    return [str(account.value) for account in possible_accounts]
