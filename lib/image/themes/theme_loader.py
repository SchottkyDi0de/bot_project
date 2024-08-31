from PIL import Image
from yaml import safe_load

from lib.data_classes.themes import Theme
from lib.data_classes.db_player import ImageSettings
from lib.settings.settings import Config

_config = Config().get()

def get_theme(theme_name: str) -> Theme:
    if theme_name == 'default':
        theme = Theme.model_validate(
            {
                'image_settings': ImageSettings.model_validate({}),
                'bg_path': _config.image.default_bg_path,
                'bg': None
            }
        )
        theme.bg = Image.open(_config.image.default_bg_path, formats=['png'])
        return theme
    else:
        with open(f'lib/image/themes/{theme_name}/props.yaml', 'r', encoding='utf-8') as file:
            raw_theme = safe_load(file)
            
        theme = Theme.model_validate(raw_theme)
        theme.bg = Image.open(theme.bg_path, formats=['png'])
        return theme
