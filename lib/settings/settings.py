import os

import yaml
from dotenv import load_dotenv, find_dotenv

from lib.data_classes.settings import Settings
from lib.utils.singleton_factory import singleton

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')


if os.path.exists(find_dotenv()):
    load_dotenv(dotenv_path)
else:
    raise Exception(
        f'Failed atempt to load enviroment variable in {dotenv_path}')

# Потенциально, можно было бы использовать https://docs.pydantic.dev/latest/concepts/pydantic_settings/
# для настроек и Pydantic вместо `python-easy-json`, но это придирка
# (Pydantic более известный и «стандартный»).
@singleton
class SttObject():
    def __init__(self) -> None:
        self.DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        self.WG_APP_ID = os.getenv('WG_APP_ID')
        self.LT_APP_ID = os.getenv('LT_APP_ID')
        with open('settings/settings.yaml', encoding='utf-8') as f:
            self.settings = Settings(yaml.safe_load(f))

        self.settings.DISCORD_TOKEN = self.DISCORD_TOKEN
        self.settings.WG_APP_ID = self.WG_APP_ID
        self.settings.LT_APP_ID = self.LT_APP_ID

    def get(self) -> Settings:
        """Return settings object"""
        return self.settings
