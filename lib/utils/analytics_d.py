from typing import Callable
from datetime import datetime

from lib.database.players import PlayersDB
from lib.data_classes.db_player import UsedCommand


def analytics(command_name: str | None = None) -> Callable:
    pdb = PlayersDB()
    def inner(func: Callable) -> Callable:
        cmd_name = command_name if command_name else func.__name__

        async def wrapper(*args, **kwargs):
            member = await pdb.get_member(args[1].from_user.id, raise_error=False)
            if member:
                await pdb.set_analytics(UsedCommand(name=cmd_name, last_used=datetime.now()), member)
            return await func(*args, **kwargs)

        return wrapper

    return inner
