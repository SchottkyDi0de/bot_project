'''Данный модуль создаёт объект, который хранит в себе локазизированныйе строки а так же метод смены локализации'''
from lib.utils.singleton_factory import singleton
from lib.settings.settings import SttObject
from lib.yaml.yaml2object import Parser
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB

from discord.ext.commands import Context

@singleton
class Text():
    def __init__(self) -> None:
        self.sdb = ServersDB()
        self.pdb = PlayersDB()
        self.default_lang = SttObject().get().default.lang
        self.current_lang = self.default_lang
        self.parser = Parser()
        self.data = self.parser.parse_file(f'locales/{self.default_lang}.yaml')
        self.load(self.default_lang)
        
    def load_from_context(self, ctx: Context) -> None:
        if self.pdb.get_member_lang(ctx.author.id) is not None:
            self.load(self.pdb.get_member_lang(ctx.author.id))
        else:
            self.load(self.sdb.safe_get_lang(ctx.guild.id))

    def load(self, lang: str) -> None:
        if self.current_lang == lang:
            return
        
        if lang in SttObject().get().default.available_locales:
            self.data = self.parser.parse_file(f'locales/{lang}.yaml')
            self.current_lang = lang
        else:
            raise ValueError(f'Invalid lang code: {lang}')
        
    def get_current_lang(self) -> str:
        return self.current_lang
        
    def get(self) -> object:
        return self.data

