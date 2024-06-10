import traceback
import pytz
from asyncio import sleep
from datetime import datetime, timedelta

from lib.api.async_wotb_api import API

from lib.data_classes.db_player import AccountSlotsEnum, SessionStatesEnum
from lib.database.players import PlayersDB
from lib.logger.logger import get_logger

_log = get_logger(__file__, 'WorkerPDBLogger', 'logs/worker_pdb.log')


class PDBWorker:
    def __init__(self):
        self.db = PlayersDB()
        self.STOP_FLAG = False
        self.api = API()

    def stop_workers(self):
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

    async def run_workers(self, *args):
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
        member_ids = await self.db.get_all_members_ids()
        print(member_ids)
        for member_id in member_ids:
            member = await self.db.get_member(member_id)
            used_slots: AccountSlotsEnum = await self.db.get_all_used_slots(member=member)
            if used_slots is None:
                continue
            
            for slot in used_slots:
                slot: AccountSlotsEnum
                session_state = await self.db.validate_session(member=member, slot=slot)
                
                if session_state != SessionStatesEnum.RESTART_NEEDED:
                    continue
                
                game_account = await self.db.get_game_account(slot, member=member)
                new_last_stats = await self.api.get_stats(game_id=game_account.game_id, region=game_account.region)
                
                _log.info(f'Session updated for {member_id} in slot {slot.name}')
                await self.db.update_session(slot, member_id, game_account.session_settings, new_last_stats)