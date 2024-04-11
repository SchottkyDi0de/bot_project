from pprint import pprint
from PIL import Image
from yaml import safe_load

from lib.data_classes.themes import Theme

def get_theme(theme_name: str) -> Theme:
    with open(f'lib/image/themes/{theme_name}/props.yaml', 'r', encoding='utf-8') as file:
        raw_theme = safe_load(file)
        theme = Theme.model_validate(raw_theme)
    theme.bg = Image.open(theme.bg_path, formats=['png'])
    return theme