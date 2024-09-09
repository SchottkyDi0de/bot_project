from __future__ import annotations

from dynamic_yaml.yaml_wrappers import YamlDict

#from lib.logger.logger import get_logger

#_log = get_logger(__file__, 'DebugLocaleLogger', 'logs/debug_locale.log')


class NotImplemented(str):
    def __new__(cls):
        return super().__new__(cls, "Not implemented")

    def __getattribute__(self, name: str) -> NotImplemented:
        get = object.__getattribute__
        if name in dir(object):
            return get(self, name)
        #_log.debug(f"Not implemented: {name}")
        return NotImplemented()
    

class Locale:
    def __init__(self, data: dict) -> None:
        self.data = data
    
    def __getattribute__(self, name: str) -> Locale | NotImplemented:
        get = object.__getattribute__

        if name in (dir(object) + ["data"]):
            return get(self, name)

        if name in get(self, "data").keys():
            dat = get(self, "data")[name]
            if isinstance(dat, YamlDict):
                return Locale(dat)

            return dat
        
        return NotImplemented()
