from asyncio import sleep

from lib.database.players import PlayersDB
from lib.logger.logger import get_logger

_log = get_logger(__name__, 'WorkerPDBLogger', 'logs/worker_pdb.log')


class PDBWorker:
    def __init__(self):
        self.db = PlayersDB()
        self.STOP_WORKER_FLAG = False

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
        self.STOP_WORKER_FLAG = True

    async def run_worker(self):
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
        while True:
            if not self.STOP_WORKER_FLAG:
                await self.check_database()
                await sleep(60 * 5)
            else:
                _log.info('WORKERS: PDB worker stopped')
                break

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

        for member_id in self.db.get_players_ids():
            if self.db.check_member(member_id):
                self.db.check_member_premium(member_id)
                self.db.check_member_last_stats(member_id)
                    