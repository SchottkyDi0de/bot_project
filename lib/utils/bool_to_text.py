from lib.locale.locale import Text

def bool_handler(data: bool) -> str:
    if data:
        return Text().get().frequent.common.yes
    else:
        return Text().get().frequent.common.no