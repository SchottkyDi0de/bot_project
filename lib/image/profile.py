from enum import Enum
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
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


class ProfileImage:
    width = 840
    height = 520


class Coords:
    nickname_block = (140, 8, ProfileImage.width - 140, 35) # (x0, y0, x1, y1)
    nickname_text = (ProfileImage.width // 2, 5) # (x, y)


class Draft:
    default = ('RGBA', (ProfileImage.width, ProfileImage.height))

class ProfileBackgrounds:
    gray = Image.open('res/image/profile/backgrounds/gray.png', formats=['png'])
    green = Image.open('res/image/profile/backgrounds/green.png', formats=['png'])
    l_blue = Image.open('res/image/profile/backgrounds/l_blue.png', formats=['png'])
    blue = Image.open('res/image/profile/backgrounds/blue.png', formats=['png'])
    purple = Image.open('res/image/profile/backgrounds/purple.png', formats=['png'])
    yellow = Image.open('res/image/profile/backgrounds/yellow.png', formats=['png'])
    orange = Image.open('res/image/profile/backgrounds/orange.png', formats=['png'])
    black = Image.open('res/image/profile/backgrounds/black.png', formats=['png'])
    g_black = Image.open('res/image/profile/backgrounds/g_black.png', formats=['png'])
    
    gray.draft(*Draft.default)
    green.draft(*Draft.default)
    l_blue.draft(*Draft.default)
    blue.draft(*Draft.default)
    purple.draft(*Draft.default)
    yellow.draft(*Draft.default)
    orange.draft(*Draft.default)
    black.draft(*Draft.default)
    g_black.draft(*Draft.default)
    

class Badges:
    active_user = Image.open('res/image/profile/badges/active_user.png', formats=['png'])
    tester = Image.open('res/image/profile/badges/tester.png', formats=['png'])
    

class Fades:
    poly_grey = Image.open('res/image/profile/textures/poly_fade.png', formats=['png'])
    poly_grey.draft(*Draft.default)


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
        self.draw_layout_map()
        self.img_draw = ImageDraw.Draw(self.img)
        
        self.draw_user_name()
        
        return img_to_base64(self.img)
    
    def draw_layout_map(self):
        layout = Image.new('RGBA', (ProfileImage.width, ProfileImage.height))
        drawable_layout = ImageDraw.Draw(layout)
        drawable_layout.rounded_rectangle(
            Coords.nickname_block,
            radius=8,
            fill=(0, 0, 0)
        )
        img_filter = ImageFilter.GaussianBlur(10)
        bg = self.img.copy()
        bg = ImageEnhance.Brightness(bg).enhance(0.5)
        bg = bg.filter(img_filter)
        self.img.paste(bg, (0, 0), layout)
        
    def draw_user_name(self) -> None:
        text = f'{self.ctx.author.display_name} | {self.ctx.author.name}'
        self.img_draw.text(
            Coords.nickname_text,
            text=text,
            fill=Colors.l_grey,
            font=Fonts.roboto_25,
            anchor='ma'
        )
        
    def draw_badges(self) -> None:
        
        
    def draw_background(self) -> None:
        user_level = get_level(self.member.profile.level_exp).level
        print(user_level)
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
        else:
            self.img = ProfileBackgrounds.gray
            
        self.img = self.img.convert('RGBA')
        # self.img = Image.alpha_composite(self.img, Fades.poly_grey)
