import elara

from lib.logger import logger
from lib.exceptions.database import TankNotFoundInTankopedia
from lib.utils.singleton_factory import singleton

_log = logger.get_logger(__file__, 'TankopediaLogger', 'logs/tankopedia.log')


@singleton
class TanksDB():
    def __init__(self) -> None:
        _log.debug('Tankopedia database initialized')
        self.db = elara.exe('database/tankopedia.eldb')
        self.cdb = elara.exe('database/custom_tankopedia.eldb')
        self.db.commit()

    def set_tankopedia(self, data: dict):
        self.db['root'] = data
        self.db['root']['id_list'] = list(data.keys())
        self.db.commit()

    def get_tank_by_id(self, id: str | int) -> dict:
        id = str(id)
        
        try:
            return self.db['root']['data'][id]
        except KeyError:
            try:
                return self.cdb['data'][id]
            except KeyError:
                _log.debug(f'Tank with id {id} not found')
                raise TankNotFoundInTankopedia()
        
    def safe_get_tank_by_id(self, id: str | int) -> dict | None:
        try:
            return self.get_tank_by_id(id)
        except TankNotFoundInTankopedia:
            return None
