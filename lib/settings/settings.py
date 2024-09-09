import os
import traceback
from itertools import cycle

import dynamic_yaml
from dotenv import find_dotenv, load_dotenv

from lib.logger.logger import get_logger
from lib.utils.singleton_factory import singleton

from lib.data_classes.settings import ConfigStruct


_log = get_logger(__file__, 'TgConfigLogger', 'logs/config.log')


_log = get_logger(__file__, 'ConfigLoaderLogger', 'logs/config_loader.log')
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
_log.debug(f'Loading environment variable in {dotenv_path}')

if not os.path.exists(find_dotenv()):
    _log.critical(f'Failed attempt to load environment variable in {dotenv_path}')
    raise FileNotFoundError(f'Failed attempt to load environment variable in {dotenv_path}')

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

#   ---------------------------------------------------------------
    
    TG_TOKEN = os.getenv('TG_TOKEN')

@singleton
class Config:
    config: ConfigStruct

    def __init__(self):
        with open('settings/settings.yaml', encoding='utf-8') as file:
            try:
                self.yaml_dict = dynamic_yaml.load(file)
                self.config = ConfigStruct.model_validate(self.yaml_dict)
            except Exception:
                _log.fatal('Failed to load settings.yaml')
                _log.fatal(traceback.format_exc())
                raise RuntimeError('Failed to load settings.yaml')
    
    def get(self) -> ConfigStruct:
        return self.config
