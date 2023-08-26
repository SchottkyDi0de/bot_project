'''Данный модуль создаёт объект, который хранит в себе все
весь текст, который должен быть локализирован.'''
import os.path, sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

from lib.yaml.yaml2object import Parser

class Text():
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Text, cls).__new__(cls)
        return cls.instance
    
    def load(self, lang: str):
        if lang in ['ru']:
            self.data = self.parser.parse(f'locales/{lang}.yaml')
        else:
            raise ValueError(f'Invalid lang code: {lang}')
            
    def __init__(self) -> None:
        self.current_lang = 'ru'
        self.parser = Parser()
        self.load(self.current_lang)
