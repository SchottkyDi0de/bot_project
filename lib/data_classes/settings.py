from typing import List, Optional, Dict

from python_easy_json import JSONObject


class Default(JSONObject):
    prefix: str
    lang: str
    available_locales: List[str]
    locale_alliases: dict[str, str]
    available_regions: List[str]


class Settings(JSONObject):
    bot_name: str
    default: Default = Default()
    session_ttl: int
