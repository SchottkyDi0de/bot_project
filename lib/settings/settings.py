import os
import traceback
from itertools import cycle
from pprint import pprint

import yaml
from dotenv import load_dotenv, find_dotenv

from lib.data_classes.settings import ConfigStruct
from lib.utils.singleton_factory import singleton
from lib.logger.logger import get_logger

_log = get_logger(__name__, 'ConfigLoaderLogger', 'logs/config_loader.log')
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if not os.path.exists(find_dotenv()):
    _log.critical(f'Failed atempt to load enviroment variable in {dotenv_path}')
    raise FileNotFoundError(f'Failed atempt to load enviroment variable in {dotenv_path}')

load_dotenv(dotenv_path)


class EnvConfig():
    DISCORD_TOKEN_DEV = os.getenv('DISCORD_TOKEN_DEV')
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

    WG_APP_ID_CL0, WG_APP_ID_CL1 = os.getenv('WG_APP_ID_CL0'), os.getenv('WG_APP_ID_CL1')
    LT_APP_ID_CL0, LT_APP_ID_CL1 = os.getenv('LT_APP_ID_CL0'), os.getenv('LT_APP_ID_CL1')

    WG_APP_IDS = cycle((WG_APP_ID_CL0, WG_APP_ID_CL1))

    LT_APP_IDS = cycle((LT_APP_ID_CL0, LT_APP_ID_CL1))

    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')

    CLIENT_ID_DEV = os.getenv('CLIENT_ID_DEV')
    CLIENT_SECRET_DEV = os.getenv('CLIENT_SECRET_DEV')

    INTERNAL_API_KEY = os.getenv('INTERNAL_API_KEY')


@singleton
class Config():
    def __init__(self) -> None:
        with open('settings/settings.yaml', encoding='utf-8') as f:
            try:
                self.yaml_dict = yaml.safe_load(f)
                self.cfg = ConfigStruct.model_validate(self.yaml_dict)
            except Exception:
                _log.critical('Failed to load settings.yaml')
                _log.critical(traceback.format_exc())
                raise RuntimeError('Failed to load settings.yaml')

    def get(self) -> ConfigStruct:
        """
        Return settings object.
        See struct in: `lib/data_classes/settings.py`
        """
        return self.cfg