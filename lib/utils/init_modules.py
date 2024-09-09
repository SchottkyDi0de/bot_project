from os import listdir

DEFAULT_IGNORE = ['__pycache__']


def init_files(path: str, ignore: list[str] | None = None) -> None:
    slash_path = path.replace(".", "/") if "." in path else path
    doted_path = path.replace("/", ".") if "/" in path else path

    if not ignore:
        ignore = []

    ignore.extend(DEFAULT_IGNORE)

    for file in listdir(slash_path):
        if file not in ignore:
            try:
                __import__(f'{doted_path}.{file[:-3] if file.endswith(".py") else file}')
            except ImportError:
                ...
