import pytz
from datetime import time, date, datetime

from lib.utils.time_converter import TimeConverter
from lib.data_classes.db_player import SessionSettings

test_data = SessionSettings(
    is_autosession=True, 
    last_get=int(datetime.now(pytz.utc).timestamp()),
    timezone=3,
    time_to_restart='03:00'
    )
    
now_date = datetime.now(pytz.utc).date()
null_time = datetime.strptime('00:00', '%H:%M').time()
restart_in = datetime.combine(now_date, null_time)

