'''Данный модуль создаёт объект, который хранит в себе локазизированныйе строки а так же метод смены локализации'''
import yaml
from discord.ext.commands import Context

from typing import Dict

from lib.data_classes.locale_struct import Localization
from lib.utils.singleton_factory import singleton
from lib.settings.settings import Config
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB

_config = Config().get()


@singleton
class Text():
    def __init__(self) -> None:
        self.sdb = ServersDB()
        self.pdb = PlayersDB()
        self.default_lang = _config.default.lang
        self.current_lang = self.default_lang
        self.datas: Dict[str, Localization] = {}

        for i in _config.default.available_locales:
            if i == 'auto':
                continue
            with open(f'locales/{i}.yaml', encoding='utf-8') as f:
                self.datas |= {i: Localization.model_validate(yaml.safe_load(f))}
        
    def load_from_context(self, ctx: Context) -> None:
        member_lang = self.pdb.get_member_lang(ctx.author.id)
        if member_lang is not None:
            self.load(member_lang)
        else:
            if ctx.interaction.locale in list(_config.default.locale_alliases.keys()):
                self.load(_config.default.locale_alliases[ctx.interaction.locale])
            else:
                self.load(self.default_lang)

    def load(self, lang: str | None) -> Localization:
        if lang not in _config.default.available_locales:
            lang = _config.default.lang
        
        if lang is None:
            lang = self.default_lang
        
        self.current_lang = lang

        return self.datas[lang]
        
    def get_current_lang(self) -> str:
        return self.current_lang

    def get(self, lang: str | None = None) -> Localization:
        if lang is None:
            return self.load(self.current_lang)
        
        return self.load(lang)
