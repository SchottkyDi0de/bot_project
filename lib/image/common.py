'''
Модуль для генерирования изображения
со статистикой
'''
import base64
from enum import Enum
from io import BytesIO
from time import time

from discord.ext.commands import Context
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import lib.api.async_wotb_api as async_wotb_api
from lib.data_classes.api.api_data import PlayerGlobalData
from lib.data_classes.db_player import ImageSettings
from lib.data_classes.db_server import ServerSettings
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.image.for_image.colors import Colors
from lib.image.for_image.fonts import Fonts
from lib.image.for_image.icons import StatsIcons
from lib.image.for_image.medals import Medals
from lib.image.themes.theme_loader import get_theme
from lib.image.for_image.watermark import Watermark
from lib.image.utils.resizer import center_crop
from lib.locale.locale import Text
from lib.logger.logger import get_logger
from lib.settings.settings import Config
from lib.utils.singleton_factory import singleton
from lib.image.for_image.stats_coloring import colorize
from lib.data_classes.db_player import DBPlayer

_log = get_logger(__file__, 'ImageCommonLogger', 'logs/image_common.log')
_config = Config().get()


class IconsCoords(Enum):
    """Class that defines the coordinates of the icons in the image."""
    # Main
    winrate: tuple[int] = (135, 110)
    avg_damage: tuple[int] = (325, 110)
    battles: tuple[int] = (532, 110)

    # Rating
    winrate_r: tuple[int] = (135, 450)
    battles_r: tuple[int] = (532, 450)

    # Total
    frags_per_battle: tuple[int] = (125, 630)
    shots: tuple[int] = (325, 630)
    xp: tuple[int] = (532, 630)
    # Line 1
    damage_ratio: tuple[int] = (128, 780)
    damage_dealt: tuple[int] = (332, 780)
    max_xp: tuple[int] = (534, 780)
    # Line 2
    destruction_ratio: tuple[int] = (125, 930)
    frags: tuple[int] = (325, 930)
    max_frags: tuple[int] = (532, 930)
    # Line 3
    avg_spotted: tuple[int] = (123, 1075)
    survived: tuple[int] = (320, 1075)
    accuracy: tuple[int] = (532, 1075)


class MedalCoords(Enum):
    """Class that defines the coordinates of the medals in the image."""
    high_caliber: tuple[int] = (105, 270)
    radley_walters: tuple[int] = (208, 270)
    mark_of_mastery: tuple[int] = (305, 270)
    medal_kolobanov: tuple[int] = (420, 270)
    warrior: tuple[int] = (526, 270)


class BackgroundRectangleMap():
    """Class that defines the coordinates of the background rectangle in the image."""
    main = (55, 85, 645, 230)
    medals = (55, 245, 645, 410)
    rating = (55, 425, 645, 575)
    total = (55, 590, 645, 1210)


class Leagues():
    """Class that represents different leagues in the application."""

    empty = Image.open('res/image/leagues/no-rating.png', formats=['png'])
    """Image representing an empty league."""

    gold = Image.open('res/image/leagues/gold.png', formats=['png'])
    """Image representing a gold league."""

    platinum = Image.open('res/image/leagues/platinum.png', formats=['png'])
    """Image representing a platinum league."""

    brilliant = Image.open('res/image/leagues/brilliant.png', formats=['png'])
    """Image representing a brilliant league."""

    calibration = Image.open('res/image/leagues/calibr.png', formats=['png'])
    """Image representing a calibration league."""


class Flags():
    eu = Image.open('res/image/flags/eu.png', formats=['png'])
    usa = Image.open('res/image/flags/usa.png', formats=['png'])
    china = Image.open('res/image/flags/china.png', formats=['png'])
    ru = Image.open('res/image/flags/ru.png', formats=['png'])


class Cache():
    cache_label = Image.open('res/image/other/cached_label.png', formats=['png'])


class Coordinates():
    def __init__(self, img_size):
        _center_x = img_size[0] // 2

        self.category_labels = {
            'main': (_center_x, 98),
            'medals': (_center_x, 257),
            'rating': (_center_x, 440),
            'total': (_center_x, 605),
        }
        self.medals_labels = {
            'mainGun': (143, 365),
            'medalRadleyWalters': (242, 365),
            'markOfMastery': (350, 365),
            'medalKolobanov': (458, 365),
            'warrior': (560, 365),
        }
        self.common_stats_labels = {
            'frags_per_battle': (150, 712),
            'damage_ratio': (150, 865),
            'destruction_ratio': (150, 1010),
            'avg_spotted': (150, 1160),

            'shots': (350, 712),
            'damage_dealt': (350, 865),
            'enemies_destroyed': (350, 1010),
            'survived_battles': (350, 1160),

            'xp': (553, 712),
            'max_xp': (553, 865),
            'max_frags': (553, 1010),
            'accuracy': (550, 1160),
        }
        self.main_labels = {
            'winrate': (150, 190),
            'avg_damage': (350, 190),
            'battles': (553, 190),
        }
        self.main_stats = {
            'winrate': (150, 175),
            'avg_damage': (350, 175),
            'battles': (553, 175),
        }
        self.rating_labels = {
            'winrate': (150, 535),
            'rating_battles': (553, 535),
        }
        self.rating_league_label = (350, 550)
        self.rating_stats = {
            'winrate': (150, 500),
            'rating': (350, 515),
            'battles': (553, 500),
        }
        self.common_stats = {
            'frags_per_battle': (150, 680),
            'damage_ratio': (150, 832),
            'destruction_ratio': (150, 976),
            'avg_spotted': (150, 1125),

            'shots': (350, 680),
            'damage_dealt': (350, 832),
            'frags': (350, 976),
            'survived_battles': (350, 1125),

            'xp': (555, 680),
            'max_xp': (553, 832),
            'max_frags': (553, 976),
            'accuracy': (550, 1125),
        }
        self.medals_count = {
            'mainGun': (143, 349),
            'medalRadleyWalters': (242, 349),
            'markOfMastery': (350, 349),
            'medalKolobanov': (458, 349),
            'warrior': (560, 349),
        }
        self.main_stats_points = {
            'winrate': (240, 108),
            'avg_damage': (410, 108),
            'battles': (610, 108),
        }
        self.rating_stats_point = {
            'battles': (235, 456),
            'winrate': (620, 456),
        }
        self.common_stats_point = {
            'frags_per_battle': (224, 615),
            'damage_ratio': (224, 690),
            'destruction_ratio': (224, 766),
            'avg_spotted': (224, 841),

            'accuracy': (620, 841),
        }


class ValueNormalizer():
    @staticmethod
    def winrate(val, enable_null=False):
        """
        Normalizes a winrate value.

        Args:
            val (float): The winrate value to normalize.

        Returns:
            str: The normalized winrate value as a string.
                  If val is 0, returns '—'.
                  Otherwise, returns the winrate value formatted as '{:.2f} %'.
        """
        if round(val, 2) == 0:
            if not enable_null:
                return '—'
            else:
                return '0'

        return '{:.2f}'.format(val) + '%'

    @staticmethod
    def ratio(val, enable_null=False):
        """
        Normalizes a ratio value.

        Args:
            val (float): The ratio value to normalize.

        Returns:
            str: The normalized ratio value as a string.
                  If val is 0, returns '—'.
                  Otherwise, returns the ratio value formatted as '{:.2f}'.
        """
        return ValueNormalizer.winrate(val, enable_null).replace('%', '')
    
    @staticmethod
    def other(val, enable_null=False, str_bypass=False):
        """
        Normalizes a value.

        Args:
            val (float or int): The value to normalize.

        Returns:
            str: The normalized value as a string.
                  If val is 0, returns '—'.
                  If val is a string, returns '—'.
                  If val is between 100,000 and 1,000,000, returns the value divided by 1,000
                    rounded to 2 decimal places and appended with 'K'.
                  If val is greater than or equal to 1,000,000, returns the value divided by 1,000,000
                    rounded to 2 decimal places and appended with 'M'.
                  Otherwise, returns the value as a string.
        """
        if str_bypass:
            if isinstance(val, str):
                return val

        if round(val) == 0:
            if not enable_null:
                return '—'
            else:
                return '0'

        if type(val) == str:
            return '—'

        index = ['K', 'M']

        if val >= 100_000 and val < 1_000_000:
            val = str(round(val / 1_000, 2)) + index[0]
        elif val >= 1_000_000:
            val = str(round(val / 1_000_000, 2)) + index[1]
        else:
            return str(val)

        return val
    
    @staticmethod
    def adaptive(value):
        '''
        Automatically selects the value normalizer based on the type of the value.
        args:
            value (float or int): The value to normalize.
        returns:
            str: The normalized value as a string.
        '''
        if isinstance(value, float):
            return ValueNormalizer.ratio(value)
        if isinstance(value, int):
            return ValueNormalizer.other(value)
        


class Values():
    def __init__(self, data: PlayerGlobalData) -> None:
        self.val_normalizer = ValueNormalizer()
        shorted_data = data.data.statistics
        self.main = {
            'winrate': self.val_normalizer.winrate(shorted_data.all.winrate),
            'avg_damage': self.val_normalizer.other(shorted_data.all.avg_damage),
            'battles': self.val_normalizer.other(shorted_data.all.battles)
        }
        self.rating = {
            'winrate': self.val_normalizer.winrate(shorted_data.rating.winrate),
            'rating': self.val_normalizer.other(shorted_data.rating.rating),
            'battles': self.val_normalizer.other(shorted_data.rating.battles)
        }
        self.common = {
            'frags_per_battle': self.val_normalizer.ratio(shorted_data.all.frags_per_battle),
            'damage_ratio': self.val_normalizer.ratio(shorted_data.all.damage_ratio),
            'destruction_ratio': self.val_normalizer.ratio(shorted_data.all.destruction_ratio),
            'avg_spotted': self.val_normalizer.ratio(shorted_data.all.avg_spotted),

            'shots': self.val_normalizer.other(shorted_data.all.shots),
            'damage_dealt': self.val_normalizer.other(shorted_data.all.damage_dealt),
            'frags': self.val_normalizer.other(shorted_data.all.frags),
            'survived_battles': self.val_normalizer.other(shorted_data.all.survived_battles),

            'xp': self.val_normalizer.other(shorted_data.all.xp),
            'max_xp': self.val_normalizer.other(shorted_data.all.max_xp),
            'max_frags': self.val_normalizer.other(shorted_data.all.max_frags),
            'accuracy': self.val_normalizer.winrate(shorted_data.all.accuracy),
        }

class ImageSize:
    max_height: int = 1300
    max_width: int = 700


@singleton
class ImageGen():
    text = None
    fonts = Fonts()
    leagues = Leagues()
    flags = Flags()
    value = None
    data = None
    diff_data = None
    image = None
    stat_all = None
    stat_rating = None
    achievements = None
    img_size = []
    coord = None
    icons = StatsIcons()
    medals = Medals()
    background_rectangles_map = BackgroundRectangleMap()
    
    def load_image(self, bytes_ot_path: str | BytesIO) -> None:
        image = Image.open(bytes_ot_path)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        self.image = center_crop(image, (ImageSize.max_width, ImageSize.max_height))

    def generate(self,
                 ctx: Context | None,
                 data: PlayerGlobalData,
                 image_settings: ImageSettings,
                 server_settings: ServerSettings,
                 debug_label: bool = False,
                 ) -> BytesIO:

        self.text = Text().get()
        start_time = time()
        pdb = PlayersDB()
        sdb = ServersDB()
        self.image_settings = image_settings

        bin_image = None
        self.data = data
        self.values = Values(data)
        self.stat_all = data.data.statistics.all
        self.stat_rating = data.data.statistics.rating
        self.achievements = data.data.achievements
        
        user_bg = pdb.get_member_image(ctx.author.id) is not None
        server_bg = sdb.get_server_image(ctx.guild.id) is not None
        allow_bg = server_settings.allow_custom_backgrounds
        
        if image_settings.theme != 'default':
            theme = get_theme(image_settings.theme)
            self.image = center_crop(theme.bg, (ImageSize.max_width, ImageSize.max_height))
            self.image_settings = theme.image_settings
        elif (image_settings.use_custom_bg or server_bg):
            if user_bg and allow_bg and image_settings.use_custom_bg:
                image_bytes = base64.b64decode(pdb.get_member_image(ctx.author.id))
                if image_bytes != None:
                    image_buffer = BytesIO(image_bytes)
                    self.load_image(image_buffer)

            elif server_bg:
                image_bytes = base64.b64decode(sdb.get_server_image(ctx.guild.id))
                if image_bytes != None:
                    image_buffer = BytesIO(image_bytes)
                    self.load_image(image_buffer)
            else:
                self.load_image(_config.image.default_bg_path)

                if self.image.mode != 'RGBA':
                    self.image.convert('RGBA').save(_config.image.default_bg_path)
                    self.load_image(_config.image.default_bg_path)
        else:
            self.load_image(_config.image.default_bg_path)

            if self.image.mode != 'RGBA':
                self.image.convert('RGBA').save('res/image/default_image/default_bg.png')
                self.load_image(_config.image.default_bg_path)

        self.image = self.image.crop((0, 50, 700, 1300))
        self.img_size = self.image.size
        self.coord = Coordinates(self.img_size)
        img_draw = ImageDraw.Draw(self.image)

        _log.debug(f'Generate model debug: image size: {self.image.size}')

        self.draw_background()
        self.draw_stats_icons()
        self.draw_medals()
        
        if data.from_cache and not image_settings.disable_cache_label:
            self.draw_cache_label(self.image)

        if not image_settings.disable_flag:
            self.draw_flag()

        self.draw_rating_icon()
        self.draw_category_labels(img_draw)
        self.draw_medals_labels(img_draw)
        self.draw_common_labels(img_draw)
        self.draw_rating_labels(img_draw)
        self.draw_nickname_box(img_draw)
        self.draw_main_labels(img_draw)
        self.draw_nickname(img_draw)

        self.draw_main_stats(img_draw)
        self.draw_rating_stats(img_draw)
        self.draw_common_stats(img_draw)
        self.draw_medal_count(img_draw)
        
        self.draw_watermark()

        if debug_label:
            self.draw_debug_label(img_draw)

        # self.draw_main_points(img_draw)
        # self.draw_rating_points(img_draw)
        # self.draw_common_points(img_draw)

        bin_image = BytesIO()
        self.image.save(bin_image, 'PNG')
        bin_image.seek(0)
        _log.debug('Image was sent in %s sec.', round(time() - start_time, 4))

        return bin_image

    def draw_stats_icons(self) -> None:
        for coord_item in IconsCoords:
            self.image.paste(getattr(self.icons, coord_item.name), coord_item.value, getattr(self.icons, coord_item.name))

    def draw_medals(self) -> False:
        for coord_item in MedalCoords:
            self.image.paste(getattr(self.medals, coord_item.name), coord_item.value, getattr(self.medals, coord_item.name))

    def draw_debug_label(self, img: ImageDraw.ImageDraw) -> None:
        bbox = img.textbbox(
            (self.img_size[0] // 2 - 150, self.img_size[1] // 2),
            text='DEBUG PREVIEW',
            font=self.fonts.roboto_40
        )
        img.rectangle(bbox, fill="grey")
        img.text(
            (self.img_size[0] // 2 - 150, self.img_size[1] // 2),
            text='DEBUG PREVIEW',
            font=self.fonts.roboto_40,
            fill=Colors.red
        )

    def draw_background(self) -> None:
        gaussian_filter = ImageFilter.GaussianBlur(radius=self.image_settings.glass_effect)
        background_map = Image.new('RGBA', (700, 1250), (0, 0, 0, 0))
        img_draw = ImageDraw.Draw(background_map)
        print(f'Image {self.image.mode} size: {self.image.size}')

        # draw nickname rectangle
        text_box = img_draw.textbbox(
            (self.img_size[0]//2, 20),
            text=self.data.data.name_and_tag,
            font=self.fonts.roboto_icons,
            anchor='ma'
        )

        text_box = list(text_box)
        text_box[0] -= 10
        text_box[2] += 10
        text_box[1] -= 5
        text_box[3] += 3

        img_draw.rounded_rectangle(
            tuple(text_box),
            radius=10,
            fill=(0, 0, 0, 20),
        )

        if not self.image_settings.disable_stats_blocks:
        # draw stats rectangles
            img_draw.rounded_rectangle(self.background_rectangles_map.main, radius=30, fill=(0, 0, 0))
            img_draw.rounded_rectangle(self.background_rectangles_map.rating, radius=30, fill=(0, 0, 0))
            img_draw.rounded_rectangle(self.background_rectangles_map.medals, radius=30, fill=(0, 0, 0))
            img_draw.rounded_rectangle(self.background_rectangles_map.total, radius=30, fill=(0, 0, 0))

        bg = self.image.copy()
        if not self.image_settings.glass_effect == 0:
            bg = bg.filter(gaussian_filter)
        if not self.image_settings.blocks_bg_opacity == 100:
            bg = ImageEnhance.Brightness(bg).enhance(self.image_settings.blocks_bg_opacity)

        self.image.paste(bg, (0, 0), background_map)

    def draw_rating_icon(self) -> None:
        rt_img = self.leagues.empty
        rating = self.stat_rating.rating
        calibration_left = self.stat_rating.calibration_battles_left

        if calibration_left == 0:
            if rating >= 3000 and rating < 4000:
                rt_img = self.leagues.gold
            if rating >= 4000 and rating < 5000:
                rt_img = self.leagues.platinum
            if rating >= 5000:
                rt_img = self.leagues.brilliant
        elif calibration_left != 10:
            rt_img = self.leagues.calibration
        else:
            rt_img = self.leagues.empty

        self.image.paste(rt_img, (326, 460), rt_img)

    def draw_nickname(self, img: ImageDraw.ImageDraw):
        if self.image_settings.hide_nickname:
            self.data.nickname = 'Player'
        if self.image_settings.hide_clan_tag:
            self.data.data.clan_tag = None
        if not self.data.data.clan_tag is None:
            tag = {
                'text':     f'[{self.data.data.clan_stats.tag}]',
                'font':     self.fonts.roboto,
            }
            nickname = {
                'text':     self.data.nickname,
                'font':     self.fonts.roboto,
            }

            tag_length = img.textlength(**tag) + 10
            nick_length = img.textlength(**nickname)
            full_length = tag_length + nick_length

            img.text(
                xy=(self.img_size[0]//2 - tag_length//2, 20),
                text=self.data.nickname,
                font=self.fonts.roboto,
                anchor='ma',
                fill=self.image_settings.nickname_color)

            img.text(
                xy=(self.img_size[0]//2 + full_length//2 - tag_length//2, 20),
                text=tag['text'],
                font=self.fonts.roboto,
                anchor='ma',
                fill=self.image_settings.clan_tag_color)
        else:
            img.text(
                (self.img_size[0]//2, 20),
                text=self.data.nickname,
                font=self.fonts.roboto,
                anchor='ma',
                fill=self.image_settings.nickname_color
            )

        img.text(
            (self.img_size[0]//2, 55),
            text=f'ID: {str(self.data.id)}',
            font=self.fonts.roboto_small2,
            anchor='ma',
            fill=Colors.l_grey)

    def draw_nickname_box(self, img: ImageDraw.ImageDraw):
        pass

    def draw_category_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.category_labels.keys():
            img.text(
                self.coord.category_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small,
                anchor='mm',
                fill=self.image_settings.main_text_color
            )

    def draw_medals_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.medals_labels.keys():
            img.text(
                self.coord.medals_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small2,
                anchor='ma',
                align='center',
                fill=self.image_settings.stats_text_color
            )

    def draw_common_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.common_stats_labels.keys():
            img.text(
                self.coord.common_stats_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small2,
                anchor='ma',
                align='center',
                fill=self.image_settings.stats_text_color
            )

    def draw_cache_label(self, img: Image.Image):
        img.paste(Cache.cache_label, (self.image.size[0] - 75, 0), Cache.cache_label)

    def draw_main_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.main_labels.keys():
            img.text(
                self.coord.main_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small2,
                anchor='ma',
                align='center',
                fill=self.image_settings.stats_text_color
            )

    def draw_rating_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.rating_labels.keys():
            img.text(
                self.coord.rating_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small2,
                anchor='ma',
                align='center',
                fill=self.image_settings.stats_text_color
            )
        self._rating_label_handler(img)

    def _rating_label_handler(self, img):
        rating = self.data.data.statistics.rating.rating
        if self.stat_rating.calibration_battles_left == 10:
            text = self.text.for_image.no_rating
        elif self.stat_rating.calibration_battles_left > 0:
            text = self.text.for_image.leagues.calibration
        elif rating >= 3000 and rating < 4000:
            text = self.text.for_image.leagues.gold
        elif rating >= 4000 and rating < 5000:
            text = self.text.for_image.leagues.platinum
        elif rating >= 5000:
            text = self.text.for_image.leagues.brilliant
        else:
            text = self.text.for_image.leagues.no_league

        img.text(
            self.coord.rating_league_label,
            text=text,
            font=self.fonts.roboto_small2,
            anchor='ma',
            # align='center',
            fill=self.image_settings.stats_text_color
        )

    def draw_main_stats(self, img: Image.Image):
        for i in self.coord.main_stats.keys():
            img.text(
                self.coord.main_stats[i],
                text=self.values.main[i],
                font=self.fonts.roboto,
                anchor='mm',
                fill=colorize(
                    i,
                    self.values.main[i],
                    self.image_settings.stats_color
                ) if self.image_settings.colorize_stats else self.image_settings.stats_color
            )

    def draw_rating_stats(self, img: Image.Image):
        for i in self.coord.rating_stats.keys():
            img.text(
                self.coord.rating_stats[i],
                text=self.values.rating[i],
                font=self.fonts.roboto,
                anchor='ma',
                fill=colorize(
                    i,
                    self.values.rating[i],
                    self.image_settings.stats_color,
                    rating=True
                ) if self.image_settings.colorize_stats else self.image_settings.stats_color
            )

    def draw_common_stats(self, img: Image.Image):
        for i in self.coord.common_stats.keys():
            img.text(
                self.coord.common_stats[i],
                text=self.values.common[i],
                font=self.fonts.roboto,
                anchor='ma',
                fill=colorize(
                    i,
                    self.values.common[i],
                    self.image_settings.stats_color
                ) if self.image_settings.colorize_stats else self.image_settings.stats_color
            )

    def draw_medal_count(self, img: Image.Image):
        for i in self.coord.medals_count.keys():
            img.text(
                self.coord.medals_count[i],
                text=str(getattr(self.achievements, i)),
                font=self.fonts.roboto_small2,
                anchor='ma',
                fill=self.image_settings.stats_color
            )

    def draw_main_points(self, img: Image.Image):
        for i in self.coord.main_stats_points.keys():
            img.text(
                self.coord.main_stats_points[i],
                text='.',
                font=self.fonts.point,
                anchor='mm',
                fill=self.point_coloring(i, getattr(self.data.data.statistics.all, i))
            )

    def draw_rating_points(self, img: Image.Image):
        for i in self.coord.main_stats_points.keys():
            img.text(
                self.coord.main_stats_points[i],
                text='.',
                font=self.fonts.point,
                anchor='mm',
                fill=self.point_coloring(i, getattr(self.data.data.statistics.all, i))
            )

    def draw_common_points(self, img: Image.Image):
        for i in self.coord.common_stats_point.keys():
            img.text(
                self.coord.common_stats_point[i],
                text='.',
                font=self.fonts.point,
                anchor='mm',
                fill=self.point_coloring(
                    i, getattr(self.data.data.statistics.all, i), rating=True)
            )
            
    def draw_watermark(self):
        self.image.paste(Watermark.v1, (
            self.img_size[0] - 40, 
            self.img_size[1] // 2 - Watermark.v1.size[1] // 2
            ), 
        Watermark.v1)

    def draw_flag(self):
        # self.data.region = 'asia' - Only for test
        match self.data.region:
            case 'ru':
                self.image.paste(self.flags.ru, (10, 10), self.flags.ru)
            case 'eu':
                self.image.paste(self.flags.eu, (10, 10), self.flags.eu)
            case 'com':
                self.image.paste(self.flags.usa, (10, 10), self.flags.usa)
            case 'asia':
                self.image.paste(self.flags.china, (10, 10), self.flags.china)