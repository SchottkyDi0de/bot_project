from discord import AutocompleteContext, OptionChoice

from lib.locale.locale import Text
from cacheout import Cache

from lib.database.players import PlayersDB
from lib.logger.logger import get_logger
from lib.utils.standard_account_validate import standard_account_validate
from lib.utils.slot_info import get_formatted_slot_info
from lib.api.async_wotb_api import API

_p_completion_cache = Cache(maxsize=10000, ttl=1200)
_log = get_logger(__file__, 'SelectorLogger', 'logs/selector.log')

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
    need_caching = False
    await Text().load_from_interaction(interaction=ctx.interaction)

    if len(ctx.value) < 3:
        return [OptionChoice(
            Text().get().completions.nickname,
            value=''
            )
        ]

    if ctx.value is not None and ctx.value.lower() in _p_completion_cache:
        _log.debug(f'cache hit {ctx.value.lower()}')
        return _p_completion_cache.get(ctx.value)
    else:
        need_caching = True
    
    players = await API().get_players_list(ctx.value.lower())
    
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
    
    if need_caching:
        _log.debug(f'cache miss {ctx.value.lower()}')
        _p_completion_cache.add(ctx.value.lower(), completions)

    if _p_completion_cache.full():
        _log.debug('cache full')

    return completions
