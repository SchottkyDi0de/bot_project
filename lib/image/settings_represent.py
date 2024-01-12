from pprint import pprint

from PIL import Image, ImageDraw, ImageChops, ImageFilter

from lib.utils.singleton_factory import singleton
from lib.data_classes.db_player import ImageSettings
from lib.image.for_iamge.colors import Colors
from lib.image.for_iamge.fonts import Fonts
from lib.locale.locale import Text
from lib.image.utils.png_trim import trim


class Offsets:
    base_offset = 40
    base_offset_y = 30
    rect_offset = 500
    line_offset_y = 70
    rect_size = 40
    after_rectangle_offset = rect_offset + base_offset + rect_size


@singleton
class SettingsRepresent:
    def __init__(self):
        self.font = Fonts().anca_coder
        self.global_offset = 0
        self.offsets = Offsets()
        
    def draw(self, image_settings: ImageSettings = ImageSettings.model_validate({})) -> Image.Image:
        image = Image.new('RGBA', (700, 1000), (100, 100, 100, 30))
        img_draw = ImageDraw.Draw(image)
        
        self.draw_text(img_draw, image_settings)
        
        image.show()
        
    def draw_text(self, img_draw: ImageDraw.ImageDraw, image_settings: ImageSettings):
        image_settings_dict = image_settings.model_dump()
        lines = 0
    
        for i in image_settings_dict.keys():
            print(getattr(Text().get('ru').cmds.image_settings_get.items, i))
            img_draw.text(
                (
                    self.offsets.base_offset, 
                    self.offsets.base_offset_y + lines * self.offsets.line_offset_y
                    ),
                text=getattr(Text().get('ru').cmds.image_settings_get.items, i),
                font=self.font,
                anchor='lm',
                align='center',
                fill=Colors().blue
            )
            lines += 1
