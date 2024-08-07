from discord import AutocompleteContext, OptionChoice

from lib.locale.locale import Text

from lib.database.players import PlayersDB
from lib.utils.standard_account_validate import standard_account_validate
from lib.utils.slot_info import get_formatted_slot_info
from lib.api.async_wotb_api import API


async def account_selector(ctx: AutocompleteContext) -> list[str]:
    await Text().load_from_interaction(interaction=ctx.interaction)
    
    member_id = ctx.interaction.user.id
    member_ctx = await standard_account_validate(account_id=member_id, slot=None)
    
    possible_accounts = await PlayersDB().get_all_used_slots(member=member_ctx[1])
    slots_info: list[str] = []
    
    for slot in possible_accounts:
        curr_account = await PlayersDB().get_game_account(slot=slot, member=member_ctx[1])
        slots_info.append(
            get_formatted_slot_info(
                slot=slot,
                text=Text().get(),
                game_account=curr_account,
                shorted=True,
                clear_md=True
            )
        )
    
    def check(account: str):
        if ctx.value.lower() in account.lower():
            return True
        return False
    
    return [slot for slot in slots_info if check(slot)]


async def global_players_selector(ctx: AutocompleteContext) -> list[OptionChoice]:
    if len(ctx.value) < 3:
        return ['Type 3 or more characters for start search']
    
    players = await API().get_players_list(ctx.value)
    
    def check(player: str):
        if ctx.value.lower() in player.lower():
            return True
        return False
    
    completions = []
    
    for key, value in players.items():
        if check(value):
            completions.append(
                OptionChoice(
                    name=value, 
                    value=str(key)
                )
            )
    
    return completions
