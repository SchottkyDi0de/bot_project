import traceback
from typing import TYPE_CHECKING
from datetime import datetime, timedelta

import pytz

from lib.logger.logger import get_logger
from lib.utils.time_converter import TimeConverter
from lib.utils.string_parser import insert_data
from lib.utils.bool_to_text import bool_handler

from lib.locale.locale import Text

from .obj import Objects

if TYPE_CHECKING:
    from lib.data_classes.api.api_data import PlayerGlobalData
    
    from lib.data_classes.db_player import AccountSlotsEnum, DBPlayer

_log = get_logger(__file__, 'TgSessionCoreLogger', 'logs/tg_session_core.log')


class SessionFunc:
    @staticmethod
    async def start_session(slot: 'AccountSlotsEnum', member: 'DBPlayer', last_stats: 'PlayerGlobalData'):
        session_settings = await Objects.pdb.get_session_settings(slot, member.id, member)
        session_settings.last_get = datetime.now(tz=pytz.utc)
        session_settings.is_autosession = False

        await Objects.pdb.start_session(slot, member.id, last_stats, session_settings)
    
    
    @staticmethod
    async def session_state(slot: 'AccountSlotsEnum', member: 'DBPlayer'):
        now_time = datetime.now(pytz.utc)
        member_id = member.id
        last_stats = await Objects.pdb.get_last_stats(slot, member_id, member)
        session_settings = await Objects.pdb.get_session_settings(slot, member_id, member)
                
                
        time_format = f'%H:' \
                            f'%M'
        long_time_format = f'%D{Text().get().frequent.common.time_units.d} | ' \
                            f'%H:' \
                            f'%M'
                
        if session_settings.last_get is None or session_settings.time_to_restart is None:
            _log.error('last_get or time_to_restart is None')
            _log.error(traceback.format_exc())
            return
                
        restart_in = session_settings.time_to_restart - (now_time + timedelta(hours=session_settings.timezone))
        time_left = (await Objects.pdb.get_session_end_time(member.current_slot, member_id, member)) - now_time
        session_time = now_time - last_stats.timestamp
                
        battles_before = last_stats.data.statistics.all.battles
        battles_after = await Objects.api.get_player_battles(last_stats.region, str(last_stats.id))

        text = insert_data(
            Text().get().cmds.session_state.items.started,
            {
                'is_autosession' : bool_handler(session_settings.is_autosession),
                'restart_in' : TimeConverter.formatted_from_secs(int(restart_in.total_seconds()), time_format) if \
                                session_settings.is_autosession else '--:--',
                'update_time' : (session_settings.time_to_restart).strftime(time_format),
                'timezone' : session_settings.timezone,
                'time': TimeConverter.formatted_from_secs(int(session_time.total_seconds()), long_time_format),
                'time_left': TimeConverter.formatted_from_secs(int(time_left.total_seconds()), long_time_format),
                'battles': str(battles_after[0] - battles_before)
            }
        )
        return text
