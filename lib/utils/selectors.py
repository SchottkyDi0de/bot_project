from discord import AutocompleteContext, OptionChoice

from lib.locale.locale import Text

from lib.database.players import PlayersDB
from lib.utils.standard_account_validate import standard_account_validate
from lib.utils.slot_info import get_formatted_slot_info
from lib.api.async_wotb_api import API


async def account_selector(ctx: AutocompleteContext, _ = None, session_required: bool = False) -> list[str]:
    if not isinstance(ctx, AutocompleteContext):
        raise TypeError(f'ctx must be an instance of AutocompleteContext, not {ctx.__class__.__name__}')
    
    await Text().load_from_interaction(interaction=ctx.interaction)
    
    member_id = ctx.interaction.user.id
    member_ctx = await standard_account_validate(account_id=member_id, slot=None)
    
    possible_accounts = await PlayersDB().get_all_used_slots(member=member_ctx[1])
    
    if session_required:
        for slot in possible_accounts:
            if not await PlayersDB().check_member_last_stats(member=member_ctx[1], slot=slot):
                possible_accounts.remove(slot)
    
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

    return slots_info

async def global_players_selector(ctx: AutocompleteContext) -> list[OptionChoice]:
    await Text().load_from_interaction(interaction=ctx.interaction)

    if len(ctx.value) < 3:
        return [OptionChoice(
            Text().get().completions.nickname,
            value=''
            )
        ]

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
                    value=f'{key} | {value.split(" | ")[0].lower()} | {value.split(" | ")[1].lower()}'
                )
            )
    
    return completions
