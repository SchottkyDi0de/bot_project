from typing import TYPE_CHECKING

from aiogram import Router

from lib.logger.logger import get_logger

from lib.utils import init_files

if TYPE_CHECKING:
    from aiogram import Dispatcher

_log = get_logger(__file__, 'TgExtensionsLogger', 'logs/tg_extensions.log')


class ExtensionsSetup:
    __funcs_filters__: list[tuple[str, tuple]] = []
    extensions: list[tuple[str, Router]] = []

    def __init__(self, _, dp: 'Dispatcher') -> None:
        init_files("extensions")
        
        for name, router in self.extensions:
            _log.info(f'Extentding `{name}`')
            dp.include_router(router)

    def __init_subclass__(cls, **_) -> None:
        _log.info(f"Loading `{cls.__name__}`")

        router = Router()
        obj = cls.__new__(cls)
        for name, filters in obj.__funcs_filters__:
            router.message.register(getattr(obj, name), *filters)
        
        getattr(obj, "init", lambda: ...)()
        getattr(obj, "__extend_router__", lambda _: ...)(router)

        ExtensionsSetup.extensions.append((cls.__name__, router))
