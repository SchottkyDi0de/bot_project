from typing import Dict

import discord
import dynamic_yaml
from discord.commands import ApplicationContext

from lib.data_classes.locale_struct import Localization
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.logger.logger import get_logger
from lib.settings.settings import Config
from lib.utils.singleton_factory import singleton

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
                self.datas |= {i: Localization.model_validate(dynamic_yaml.load(f))}
    
    async def load_from_context(self, ctx: ApplicationContext) -> None:
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
        
        lang = await self.pdb.get_lang(ctx.author.id)

        if lang is not None:
            self.load(lang)
        elif ctx.interaction.locale in list(_config.default.locale_aliases.keys()):
            self.load(_config.default.locale_aliases[ctx.interaction.locale])
        else:
            self.load(self.default_lang)
            
    async def load_from_interaction(self, interaction: discord.Interaction) -> None:
        """
        Loads the language based on the given interaction.

        Args:
            interaction (discord.Interaction): The interaction object containing information about the user.

        Returns:
            None
        """
        if not isinstance(interaction, discord.Interaction):
            _log.error(f'interaction must be an instance of discord.Interaction, not {interaction.__class__.__name__}')
            raise TypeError(f'interaction must be an instance of discord.Interaction, not {interaction.__class__.__name__}')
        
        lang = await self.pdb.get_lang(interaction.user.id)

        if lang is not None:
            self.load(lang)
        elif interaction.locale in list(_config.default.locale_aliases.keys()):
            self.load(_config.default.locale_aliases[interaction.locale])
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
            lang = self.default_lang
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