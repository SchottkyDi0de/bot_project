from typing import List

from python_easy_json import JSONObject


class Default(JSONObject):
    prefix: str = None
    lang: str = None
    available_locales: List[str]


class Settings(JSONObject):
    bot_name: str = None
    default: Default = None
