from lib.locale.locale import Text


def bool_handler(data: bool) -> str:
    return (Text().get().frequent.common.no, Text().get().frequent.common.yes)[not not data]
