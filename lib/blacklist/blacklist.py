from discord import ApplicationContext

from lib.exceptions.blacklist import UserBanned
from lib.database.internal import InternalDB


async def check_user(ctx: ApplicationContext | int):
    """
    Checks if the user is in the block list and raises UserBanned exception if they are.

    Args:
        ctx (Context): The context object containing information about the user.

    Raises:
        UserBanned: If the user is in the block list.

    Returns:
        None
    """
    p_id = ctx.author.id if isinstance(ctx, ApplicationContext) else ctx
    
    if await InternalDB().check_ban(p_id):
        raise UserBanned
