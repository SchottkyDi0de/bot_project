from datetime import datetime
from typing import TYPE_CHECKING

import pytz
from aiogram.types import BufferedInputFile

from lib.data_parser.parse_data import get_session_stats

from lib.image import SessionImageGen

from .obj import Objects

if TYPE_CHECKING:
    from lib.data_classes.db_player import AccountSlotsEnum


class SessionImageGenFunc:
    async def generate_image(slot: 'AccountSlotsEnum', author_id: int) -> BufferedInputFile:
        member = await Objects.pdb.get_member(author_id)
        account = member.game_accounts.get_account_by_slot(slot)
        session_settings = await Objects.pdb.get_session_settings(slot, author_id, member)

        stats = await Objects.api.get_stats(
            game_id=account.game_id, 
            region=account.region,
            requested_by=member
        )

        last_stats = await Objects.pdb.get_last_stats(slot, author_id, member)
            
        session_settings.last_get = datetime.now(pytz.utc)
        await Objects.pdb.set_session_settings(slot, author_id, session_settings)

        diff_stats = await get_session_stats(last_stats, stats)
    
        return BufferedInputFile(
            (SessionImageGen().generate(
                data=stats, 
                diff_data=diff_stats,
                player=member,
                slot=slot,
                )).getvalue(), 
            filename='session.png'
        )
