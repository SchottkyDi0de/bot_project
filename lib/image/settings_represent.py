from pprint import pprint

from PIL import Image, ImageDraw, ImageChops, ImageFilter

from lib.utils.singleton_factory import singleton
from lib.data_classes.db_player import ImageSettings
from lib.image.common import Fonts, Colors
from lib.locale.locale import Text
from lib.image.utils.png_trim import trim


@singleton
class SettingsRepresent:
    def __init__(self):
        self.font = Fonts.roboto
        self.global_offset = 0
        
    def coords_definer(self, image_settings: ImageSettings = ImageSettings.model_validate({})):
        base_offset = 40
        self.global_offset = base_offset
        base_offset_y = 30
        rect_offset = 500
        line_offset_y = 70
        rect_size = 40
        after_rectangle_offset = rect_offset + base_offset + rect_size
        lines = 0
        coord_map: dict[str, object] = {}
        image = Image.new('RGBA', (1000, 1000), (100, 100, 100, 30))
        img_draw = ImageDraw.Draw(image)
        
        offset = base_offset
        for key, value in image_settings.model_dump().items():
            coord_map[key + '!text'] = (0, offset)
            if 'color' in key:
                coord_map[key + '!rect'] = (
                    rect_offset, offset - rect_size // 2,
                    rect_offset + rect_size, offset + rect_size // 2
                )
                
            offset += line_offset_y
                
        for key, value in coord_map.items():
            if '!text' in key:
                img_draw.text(
                    value, 
                    text=key.replace('!text', '').upper(), 
                    font=self.font,
                    anchor='lm',
                    fill=(255, 255, 255, 255)
                    )
                .
            if '!rect' in key:
                img_draw.rectangle((value[0], value[1], value[0] + rect_size, value[1] + rect_size), fill=(255, 255, 255))
                
        image.show()
        
        def draw_text():
        
        
                