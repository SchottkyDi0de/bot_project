import elara

from lib.logger import logger
from lib.exceptions.database import TankNotFoundInTankopedia

_log = logger.get_logger(__name__, 'TankopediaLogger', 'logs/tankopedia.log')

class TanksDB():
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(TanksDB, cls).__new__(cls)
        return cls.instance
    
    def __init__(self) -> None:
        _log.debug('Takopedia database initialized')
        self.db = elara.exe('database/tankopedia.eldb')

    def set_tankopedia(self, data: dict):
        self.db['root'] = data
        self.db['root']['id_list'] = list(data['data'].keys())
        self.db.commit()

    def get_tank_by_id(self, id: str) -> dict:
        _log.debug(f'Retrieving tank with id {id}')
        if id in self.db['root']['id_list']:
            return self.db['root']['data'][id]
        else:
            raise TankNotFoundInTankopedia
