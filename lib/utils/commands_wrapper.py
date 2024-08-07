from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from discord import ApplicationContext

from lib.data_classes.db_player import AccountSlotsEnum, UsedCommand
from lib.data_classes.member_context import MemberContext, MixedApplicationContext
from lib.utils.standard_account_validate import standard_account_validate
from lib.locale.locale import Text
from lib.database.players import PlayersDB
from lib.exceptions.database import InvalidSlot

P = ParamSpec('P')
T = TypeVar('T')

def with_user_context_wrapper(
    cmd_name: str,
    premium: bool = False, 
    verified: bool = False, 
    ban_check: bool = True,
    need_session: bool = False,
    allow_empty_slot: bool = False,
    slot_param_name: str = 'account',
    use_defer: bool = True
    ) -> Callable[P, Awaitable[T]]:
    """
    Decorator function that wraps a command function with user context validation.

    Args:
        cmd_name (str): The name of the command function.
        premium (bool, optional): Whether to check if the user has premium. Defaults to False.
        verified (bool, optional): Whether to check if the user is verified. Defaults to False.
        ban_check (bool, optional): Whether to check if the user is banned. Defaults to True.
        need_session (bool, optional): Whether to check if the user has an active session. Defaults to False.
        allow_empty_slot (bool, optional): Whether to allow an empty slot. Defaults to False.
        slot_param_name (str, optional): The name of the slot parameter. Defaults to 'account'.

    Returns:
        Callable: A decorator function that wraps the command function with user context validation.
        
    # Note: 
    ### This decorator inject a MixedApplicationContext object as the first argument of the wrapped function.
    """
    def decorator(wrapped_func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
        @wraps(wrapped_func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            account = kwargs.get(slot_param_name, None)
            ctx: ApplicationContext = args[1]
            
            await Text().load_from_context(ctx)
            
            if use_defer:
                await ctx.defer()
            
            if account is not None:
                try:
                    account = int(account[-1])
                except (IndexError, ValueError, TypeError):
                    raise InvalidSlot
                else:
                    if account not in [x.value for x in AccountSlotsEnum]:
                        raise InvalidSlot 
            
            game_account, member, slot = await standard_account_validate(
                account_id=ctx.author.id, 
                slot=account, 
                check_premium=premium,
                check_banned=ban_check,
                check_verified=verified,
                check_active_session=need_session,
                allow_empty_slot=allow_empty_slot
            )
            await PlayersDB().set_analytics(UsedCommand(name=ctx.command.name), member=member)
            member_context = MemberContext(member=member, game_account=game_account, slot=slot)
            mixed_context = MixedApplicationContext(m_ctx=member_context, ctx=ctx)
            new_args = (args[0], mixed_context) + args[2:]
            await wrapped_func(*new_args, **kwargs)

        wrapper.__name__ = cmd_name
        return wrapper
        
    return decorator 