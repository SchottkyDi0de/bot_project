import pytz
from asyncio import sleep
from datetime import datetime, time, timedelta

from lib.api.async_wotb_api import API

from lib.database.players import PlayersDB
from lib.logger.logger import get_logger
from lib.utils.time_converter import TimeConverter

_log = get_logger(__file__, 'WorkerPDBLogger', 'logs/worker_pdb.log')


class PDBWorker:
    def __init__(self):
        self.db = PlayersDB()
        self.STOP_FLAG = False
        self.api = API()

    def stop_worker(self):
        """
        Stop the worker.

        This function sets the STOP_WORKER_FLAG to True, indicating that the worker should stop processing tasks.

        Parameters:
            None

        Returns:
            None
        """
        _log.debug('WORKERS: setting STOP_WORKER_FLAG to True')
        self.STOP_FLAG = True

    async def run_worker(self, *args):
        """
        Asynchronously runs the worker in a loop.

        This function continuously checks the database and sleeps for 5 minutes
        before checking again. It stops running when the STOP_WORKER_FLAG is set
        to True.

        Parameters:
            None

        Returns:
            None
        """
        _log.info('WORKERS: PDB worker started')
        
        while not self.STOP_FLAG:
            await self.check_database()
            await sleep(60 * 5)
            
        _log.info('WORKERS: PDB worker stopped')

    async def check_database(self) -> None:
        """
        Check the database for any outdated data and update it if necessary.
        This function iterates over all the member IDs in the database and checks the data timestamp for each member.
        If the data is outdated, it updates the data for that member.
        It also checks the premium status for each member.

        Parameters:
            None

        Returns:
            None: This function does not return anything.
        """
        member_ids = self.db.get_players_ids()
        for member_id in member_ids:
            player = self.db.get_member(member_id)
            
            if self.db.check_member_last_stats(member_id):
                self.db.validate_session(member_id)
            else:
                continue
            
            session_settings = self.db.get_member_session_settings(member_id)
            self.db.check_member_premium(member_id)
            
            if session_settings.is_autosession:
                now_time = datetime.now(pytz.utc)
                
                if now_time > (session_settings.time_to_restart - timedelta(hours=session_settings.timezone)):
                    session_settings.time_to_restart += timedelta(days=1)
                    last_stats = await self.api.get_stats(region=player.region, game_id=player.game_id)
                    self.db.start_autosession(member_id, last_stats, session_settings)
                
            await sleep(0.05)