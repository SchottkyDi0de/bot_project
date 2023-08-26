import sys
import os

from dotenv import load_dotenv

if __name__ == '__main__':
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, path)
    
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

from lib.yaml.yaml2object import Parser

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    raise Exception(f'Failed atempt to load enviroment variable into {dotenv_path}')


class SttInit():
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SttInit, cls).__new__(cls)
        return cls.instance
    
    def __init__(self) -> None:
        self.parser = Parser()
        self.DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        self.WG_APP_ID = os.getenv('WG_APP_ID')
        self.LT_APP_ID = os.getenv('LT_APP_ID')
        self.settings = self.parser.parse('settings/settings.yaml')
        self.settings.DISCORD_TOKEN = self.DISCORD_TOKEN
        self.settings.WG_APP_ID = self.WG_APP_ID
        self.settings.LT_APP_ID = self.LT_APP_ID

    def get(self) -> object:
        """Return settings object"""
        return self.settings
