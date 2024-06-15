from enum import Enum
from PIL import Image, ImageDraw, ImageFilter
from discord import ApplicationContext

from lib.data_classes.db_player import DBPlayer, ImageSettings
from lib.data_classes.locale_struct import Localization
from lib.image.utils.resizer import resize_image
from lib.image.utils.b64_img_handler import img_to_base64
from lib.utils.calculate_exp import get_level
from lib.utils.singleton_factory import singleton
from lib.locale.locale import Text
from lib.image.for_image.fonts import Fonts
from lib.image.for_image.colors import Colors


class ProfileBackgrounds:
    gray = Image.open('res/image/profile/backgrounds/bg_0.png', formats=['png'])
    green = Image.open('res/image/profile/backgrounds/bg_1.png', formats=['png'])
    l_blue = Image.open('res/image/profile/backgrounds/bg_2.png', formats=['png'])
    blue = Image.open('res/image/profile/backgrounds/bg_3.png', formats=['png'])
    purple = Image.open('res/image/profile/backgrounds/bg_4.png', formats=['png'])
    yellow = Image.open('res/image/profile/backgrounds/bg_5.png', formats=['png'])
    orange = Image.open('res/image/profile/backgrounds/bg_6.png', formats=['png'])
    black = Image.open('res/image/profile/backgrounds/bg_7.png', formats=['png'])
    g_black = Image.open('res/image/profile/backgrounds/bg_8.png', formats=['png'])


class ProfileImage(Enum):
    width = 840
    height = 520

@singleton
class ProfileImageGen:
    def __init__(self) -> None:
        self.text: Localization = None
        self.img: Image.Image = None
        self.img_draw: ImageDraw.ImageDraw = None
        self.member: DBPlayer = None
        self.ctx: ApplicationContext = None
        
    def generate(self, member: DBPlayer, ctx: ApplicationContext) -> str:
        self.member = member
        self.ctx = ctx
        self.text = Text().get()
        
        self.draw_background()
        self.img_draw = ImageDraw.Draw(self.img)
        
        self.draw_user_name()
        
        return img_to_base64(self.img)
        
    def draw_user_name(self) -> None:
        pos = (self.img.size[0] // 2, 5)
        self.img_draw.text(
            pos,
            text=f'{self.ctx.author.display_name} | {self.ctx.author.name}',
            fill=Colors.l_grey,
            font=Fonts.roboto_25,
            anchor='ma'
        )
        
    def draw_background(self) -> None:
        user_level = get_level(self.member.profile.level_exp).level
        if 0 <= user_level < 2:
            self.img = ProfileBackgrounds.gray
        elif 2 <= user_level < 5:
            self.img = ProfileBackgrounds.green
        elif 5 <= user_level < 8:
            self.img = ProfileBackgrounds.l_blue
        elif 8 <= user_level < 12:
            self.img = ProfileBackgrounds.blue
        elif 12 <= user_level < 15:
            self.img = ProfileBackgrounds.purple
        elif 15 <= user_level < 18:
            self.img = ProfileBackgrounds.yellow
        elif 18 <= user_level < 20:
            self.img = ProfileBackgrounds.orange
        elif 20 <= user_level < 25:
            self.img = ProfileBackgrounds.black
        elif 25 <= user_level:
            self.img = ProfileBackgrounds.g_black
