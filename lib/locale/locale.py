from typing import Dict
import discord

import yaml
from discord.commands import ApplicationContext

from lib.data_classes.locale_struct import Localization
from lib.logger.logger import get_logger
from lib.utils.singleton_factory import singleton
from lib.settings.settings import Config
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB

_config = Config().get()
_log = get_logger(__file__, 'LocaleLogger', 'logs/locale.log')


@singleton
class Text():
    def __init__(self) -> None:
        """
        Initializes the Text object.

        Returns:
            None
        """
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
    
    def load_from_context(self, ctx: ApplicationContext) -> None:
        """
        Loads the language based on the given context.

        Args:
            ctx (Context): The context object containing information about the user.

        Returns:
            None
        """
        if not isinstance(ctx, discord.commands.ApplicationContext):
            _log.error(f'ctx must be an instance of discord.commands.ApplicationContext, not {ctx.__class__.__name__}')
            raise TypeError(f'ctx must be an instance of discord.commands.ApplicationContext, not {ctx.__class__.__name__}')
        
        member_lang = self.pdb.get_member_lang(ctx.author.id)
        if member_lang is not None:
            self.load(member_lang)
        else:
            if ctx.interaction.locale in list(_config.default.locale_aliases.keys()):
                self.load(_config.default.locale_aliases[ctx.interaction.locale])
            else:
                self.load(self.default_lang)
    
    def load(self, lang: str | None) -> Localization:
        """
        Loads the specified language.

        Args:
            lang (str | None): The language to load.

        Returns:
            Localization: The loaded language data.
        """
        if lang not in _config.default.available_locales:
            lang = _config.default.lang
        if lang is None:
            lang = self.default_lang
            
        self.current_lang = lang
        return self.datas[lang]
    
    def get_current_lang(self) -> str:
        """
        Gets the currently loaded language.

        Returns:
            str: The currently loaded language.
        """
        return self.current_lang
    
    def get(self, lang: str | None = None) -> Localization:
        """
        Gets the language data for the specified language.

        Args:
            lang (str | None): The language to get the data for. If None, uses the currently loaded language.

        Returns:
            Localization: The language data.
        """
        if lang is None:
            return self.load(self.current_lang)
        return self.load(lang)