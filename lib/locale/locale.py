'''Данный модуль создаёт объект, который хранит в себе локазизированныйе строки а так же метод смены локализации'''
import os.path
import sys

# path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# sys.path.insert(0, path)

from lib.settings.settings import SttInit
from lib.yaml.yaml2object import Parser


class Text():
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Text, cls).__new__(cls)
        return cls.instance

    def load(self, lang: str) -> None:
        if lang in SttInit().get().default.available_locales:
            self.data = self.parser.parse(f'locales/{lang}.yaml')
        else:
            raise ValueError(f'Invalid lang code: {lang}')
        
    def get(self) -> object:
        return self.data

    def __init__(self) -> None:
        self.current_lang = 'ru'
        self.parser = Parser()
        self.load(self.current_lang)
