from typing import Dict

import dynamic_yaml

from aiogram.types import Message, User, CallbackQuery

from lib.data_classes.locale_struct import Localization
from lib.data_classes.db_player import DBPlayer
from lib.logger.logger import get_logger
from lib.settings.settings import Config
from lib.utils.singleton_factory import singleton

from .debug import Locale

_config = Config().get()
_log = get_logger(__file__, 'LocaleLogger', 'logs/tg_locale.log')


@singleton
class Text():
    def __init__(self) -> None:
        """
        Initializes the Text object.

        Returns:
            None
        """
        self.default_lang = _config.default.lang
        self.current_lang = self.default_lang
        self.datas: Dict[str, Localization | Locale] = {}
        for i in _config.default.available_locales:
            if i == 'auto':
                continue
            with open(f'locales/{i}.yaml', encoding='utf-8') as f:
                data = dynamic_yaml.load(f)
                if __debug__:
                    self.datas |= {i: Locale(data)}
                else:
                    self.datas |= {i: Localization.model_validate(data)}
    
    async def load_by_data(self, data: Message | User | CallbackQuery, member: DBPlayer | None) -> None:
        """
        Loads the language based on the given Message | User obj.

        Args:
            data: The Message | User | CallbackQuery object containing information about the user.

        Returns:
            None
        """
        if not isinstance(data, Message | User | CallbackQuery):
            _log.error('data must be an instance of aiogram.types.Message | aiogram.types.User ' \
                       f'| aiogram.types.CallbackQuery, not {data.__class__.__name__}')
            raise TypeError('data must be an instance of aiogram.types.Message | aiogram.types.User ' \
                            f'| aiogram.types.CallbackQuery, not {data.__class__.__name__}')
        
        member_lang = member.lang if member else None
        if member_lang is not None:
            self.load(member_lang)
        else:
            language_code = data.language_code if isinstance(data, User) else data.from_user.language_code
            if language_code is not None:
                language_code = language_code.split("-")[0]
                language_code = language_code if language_code in _config.default.available_locales else None
            self.load(language_code or self.default_lang)
    
    async def load_by_id(self, member: DBPlayer | None, language_code: None | str=None) -> None:
        """
        Loads the language based on the given ID.

        Args:
            id (int): The ID of the user.

        Returns:
            None
        """
        if member is None:
            member = type("Placeholder", (), {"lang": None})
        if isinstance(language_code, str):
            language_code = language_code.split("-")[0]
        
        self.load(member.lang or \
                  (language_code if language_code in _config.default.available_locales else \
                    None or self.default_lang))
    
    def load(self, lang: str | None) -> Localization | Locale:
        """
        Loads the specified language.

        Args:
            lang (str | None): The language to load.

        Returns:
            Localization: The loaded language data.
        """
        if lang not in _config.default.available_locales:
            lang = _config.default.lang
            
        self.current_lang = lang
        return self.datas[lang]
    
    def get_current_lang(self) -> str:
        """
        Gets the currently loaded language.

        Returns:
            str: The currently loaded language.
        """
        return self.current_lang
    
    def get(self, lang: str | None = None) -> Localization | Locale:
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