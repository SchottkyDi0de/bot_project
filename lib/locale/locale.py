'''Данный модуль создаёт объект, который хранит в себе локазизированныйе строки а так же метод смены локализации'''
import os.path
import sys

from lib.utils.singleton_factory import singleton
from lib.settings.settings import SttObject
from lib.yaml.yaml2object import Parser

@singleton
class Text():
    def __init__(self) -> None:
        self.default_lang = SttObject().get().default.lang
        self.current_lang = self.default_lang
        self.parser = Parser()
        self.data = self.parser.parse_file(f'locales/{self.default_lang}.yaml')
        self.load(self.default_lang)

    def load(self, lang: str) -> None:
        if self.current_lang == lang:
            return
        
        if lang in SttObject().get().default.available_locales:
            self.data = self.parser.parse_file(f'locales/{lang}.yaml')
            self.current_lang = lang
        else:
            raise ValueError(f'Invalid lang code: {lang}')
        
    def get(self) -> object:
        return self.data

