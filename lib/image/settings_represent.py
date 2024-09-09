from io import BytesIO
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from lib.image.for_image.colors import Colors
from lib.image.for_image.fonts import Fonts
from lib.utils.bool_to_text import bool_handler
from lib.utils.singleton_factory import singleton

from lib.locale.locale import Text

if TYPE_CHECKING:
    from lib.data_classes.db_player import ImageSettings


class Offsets:
    base_offset = 40
    base_offset_y = 30
    rect_offset = 550
    rect_center_offset = rect_offset + 55
    line_offset_y = 60
    rect_size = 40
    after_rectangle_offset = rect_offset + rect_size


@singleton
class SettingsRepresent:
    def __init__(self):
        self.font = Fonts.anca_coder
        self.small_font = Fonts.anca_coder_16
        self.global_offset = 0
        self.offsets = Offsets()
        self.image = None
        self.img_draw = None
        
    def draw(self, image_settings: 'ImageSettings') -> BytesIO:
        self.image = Image.new('RGBA', (700, 950), (40, 40, 40, 255))
        self.img_draw = ImageDraw.Draw(self.image)
        
        self.draw_text(self.img_draw, image_settings)
        self.draw_v_line(self.img_draw)
        self.draw_h_lines(self.img_draw, image_settings)
        self.draw_color_represent(self.img_draw, image_settings)
        self.draw_bool_values(self.img_draw, image_settings)
        self.draw_block_bg_opacity_repr(image_settings)
        self.draw_glass_effect_repr(image_settings)
        self.draw_theme_repr(self.img_draw, image_settings)
        
        if image_settings.disable_stats_blocks:
            self.inactive_block_bg_settings(image_settings)
        
        bin_image = BytesIO()
        self.image.save(bin_image, 'PNG')
        bin_image.seek(0)

        return bin_image

    def draw_v_line(self, img_draw: ImageDraw.ImageDraw):
        img_draw.line(
            xy=(
                self.offsets.rect_offset - self.offsets.base_offset,
                0,
                self.offsets.rect_offset - self.offsets.base_offset,
                1000
            ),
            fill=Colors.blue,
            width=2
        )
        
    def inactive_block_bg_settings(self, image_settings: 'ImageSettings'):
        image_settings: dict = image_settings.model_dump()
        gaussian_filter = ImageFilter.GaussianBlur(2)
        bg = self.image.copy().filter(gaussian_filter)
        bg = ImageEnhance.Brightness(bg).enhance(0.5)
        rect_map = Image.new('RGBA', self.image.size, color=(0, 0, 0, 0))
        img_draw = ImageDraw.Draw(rect_map)
        bg.filter(gaussian_filter)
        
        for index, key in enumerate(image_settings.keys()):
            if key == 'disable_stats_blocks':
                img_draw.rounded_rectangle(
                    (
                        0,
                        self.offsets.line_offset_y * (index + 1) + 3,
                        self.image.size[0],
                        self.offsets.line_offset_y * (index + 3) - 3
                    ),
                    radius=8,
                    fill='black'
                )
                self.image.paste(bg, (0, 0), rect_map)
                self.img_draw.text(
                    (
                        self.image.size[0] // 2,
                        self.offsets.line_offset_y * (index + 2),
                    ), 
                    text=Text().get().cmds.image_settings.settings_represent_alias.items.stats_blocks_disabled.upper(),
                    anchor='mm',
                    fill=Colors.red,
                    font=self.font
                )
    
    def draw_h_lines(self, img_draw: ImageDraw.ImageDraw, image_settings: 'ImageSettings'):
        settings_count = len(image_settings.model_dump())
        for i in range(settings_count):
            i += 1
            img_draw.line(
                xy=(
                    0,
                    self.offsets.line_offset_y * i,
                    700,
                    self.offsets.line_offset_y * i
                ),
                fill=Colors.blue,
                width=2
            )
            
    def draw_color_represent(self, img_draw: ImageDraw.ImageDraw, image_settings: 'ImageSettings'):
        image_settings: dict = image_settings.model_dump()
        for index, (key, value) in enumerate(image_settings.items()):
            if '_color' in key:
                img_draw.rounded_rectangle(
                    (
                        self.offsets.rect_offset - self.offsets.rect_size // 2,
                        self.offsets.line_offset_y * index - self.offsets.rect_size // 2 + self.offsets.base_offset_y,
                        self.offsets.rect_offset + self.offsets.rect_size // 2,
                        self.offsets.line_offset_y * index + self.offsets.rect_size // 2 + self.offsets.base_offset_y,
                    ),
                    fill=image_settings[key],
                    radius=4
                )
                img_draw.text(
                    (
                        self.offsets.after_rectangle_offset,
                        self.offsets.line_offset_y * index + self.offsets.base_offset_y
                    ),
                    text=value.upper(),
                    anchor='lm',
                    fill=Colors.grey,
                    font=self.font
                )
        
    def draw_bool_values(self, img_draw: ImageDraw.ImageDraw, image_settings: 'ImageSettings'):
        image_settings: dict = image_settings.model_dump()
        index = 0
        for index, value in enumerate(image_settings.values()):
            if isinstance(value, bool):
                img_draw.text(
                    (
                        self.offsets.rect_offset, 
                        self.offsets.base_offset_y + index * self.offsets.line_offset_y
                    ),
                    text=bool_handler(value),
                    font=self.font,
                    anchor='lm',
                    align='center',
                    fill=Colors.l_green if value else Colors.l_red
                )
            index += 1
    
    def draw_theme_repr(self, img_draw: ImageDraw.ImageDraw, image_settings: 'ImageSettings'):
        image_settings: dict = image_settings.model_dump()
        index = 0
        for index, (key, value) in enumerate(image_settings.items()):
            if key == 'theme':
                img_draw.text(
                    (
                        self.offsets.rect_center_offset, 
                        self.offsets.base_offset_y + index * self.offsets.line_offset_y
                    ),
                    text=value.upper().replace('_', ' '),
                    font=self.font,
                    anchor='mm',
                    align='center',
                    fill=Colors.grey
                )
            index += 1
    
    def draw_text(self, img_draw: ImageDraw.ImageDraw, image_settings: 'ImageSettings'):
        image_settings_dict = image_settings.model_dump()
        lines = 0
    
        for i in image_settings_dict.keys():
            img_draw.text(
                (
                    self.offsets.base_offset, 
                    self.offsets.base_offset_y + lines * self.offsets.line_offset_y
                    ),
                text=getattr(Text().get().cmds.image_settings.settings_represent_alias.items, i).upper(),
                font=self.font,
                anchor='lm',
                align='center',
                fill=Colors.blue
            )
            lines += 1
        
    def draw_block_bg_opacity_repr(self, image_settings: 'ImageSettings'):
        image_settings: dict = image_settings.model_dump()
        bg = self.image.copy()
        img_draw = ImageDraw.Draw(bg)
        for index, (key, value) in enumerate(image_settings.items()):
            if key == 'stats_blocks_transparency':
                self.img_draw.text(
                    (
                        self.offsets.rect_offset + 1, 
                        self.offsets.base_offset_y + index * self.offsets.line_offset_y
                    ),
                    font=self.font,
                    anchor='mm',
                    align='center',
                    text='BG'
                )
                img_draw.rounded_rectangle(
                    (
                        self.offsets.rect_offset - self.offsets.rect_size // 2,
                        self.offsets.line_offset_y * index - self.offsets.rect_size // 2 + self.offsets.base_offset_y,
                        self.offsets.rect_offset + self.offsets.rect_size // 2,
                        self.offsets.line_offset_y * index + self.offsets.rect_size // 2 + self.offsets.base_offset_y,
                    ),
                    fill=(0, 0, 0, 255 - int(255*value)),
                    radius=4
                )
                img_draw.text(
                    (
                        self.offsets.after_rectangle_offset,
                        self.offsets.base_offset_y + index * self.offsets.line_offset_y
                    ),
                    text=str(value*100)+'%',
                    anchor='lm',
                    font=self.font,
                    fill=Colors.blue
                )
        self.image.alpha_composite(bg)
        
    def draw_glass_effect_repr(self, image_settings: 'ImageSettings'):
        image_settings: dict = image_settings.model_dump()
        bg = None
        rect_map = None
        for index, (key, value) in enumerate(image_settings.items()):
            if key == 'glass_effect':
                self.img_draw.line(
                    (
                        self.offsets.rect_offset - 30,
                        self.offsets.base_offset_y + index * self.offsets.line_offset_y,
                        self.offsets.rect_offset + 30,
                        self.offsets.base_offset_y + index * self.offsets.line_offset_y,
                    ),
                    fill=Colors.l_green,
                    width=10
                )
                gaussian_filter = ImageFilter.GaussianBlur(value)
                bg = self.image.copy().filter(gaussian_filter)
                bg = ImageEnhance.Brightness(bg).enhance(image_settings['stats_blocks_transparency'])
                rect_map = Image.new('RGBA', self.image.size, (0, 0, 0, 0))
                img_draw = ImageDraw.Draw(rect_map)
                img_draw.rounded_rectangle(
                    (
                        self.offsets.rect_offset - self.offsets.rect_size // 2,
                        self.offsets.line_offset_y * index - self.offsets.rect_size // 2 + self.offsets.base_offset_y,
                        self.offsets.rect_offset + self.offsets.rect_size // 2,
                        self.offsets.line_offset_y * index + self.offsets.rect_size // 2 + self.offsets.base_offset_y,
                    ),
                    fill='black',
                    radius=4
                )
                self.img_draw.text(
                    (
                        self.offsets.after_rectangle_offset,
                        self.offsets.base_offset_y + index * self.offsets.line_offset_y
                    ),
                    text=str(value)+'px',
                    anchor='lm',
                    font=self.font,
                    fill=Colors.blue
                )
        
        if bg is not None and rect_map is not None:
            self.image.paste(bg, (0, 0), rect_map)
        else:
            raise KeyError('Key "glass_effect" not in image_settings')
