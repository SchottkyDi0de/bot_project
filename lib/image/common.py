'''
Модуль для генерирования изображения
со статистикой.
'''
from datetime import datetime
from io import BytesIO
import base64
from time import time

from cacheout import FIFOCache
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from discord.ext.commands import Context

from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
import lib.api.async_wotb_api as async_wotb_api
from lib.data_classes.api_data import PlayerGlobalData
from lib.locale.locale import Text
from lib.logger import logger
from lib.utils.singleton_factory import singleton
from lib.locale.locale import Text
from lib.image.for_iamge.icons import StatsIcons
from lib.image.for_iamge.medals import Medals

_log = logger.get_logger(__name__, 'ImageCommonLogger',
                         'logs/image_common.log')


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
    kills_per_battle: tuple[int] = (125, 630)
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
    main = (25, 85, 675, 230)
    medals = (25, 245, 675, 410)
    rating = (25, 425, 675, 575)
    total = (25, 590, 675, 1210)

class Fonts():
    """Class that defines different fonts used in the application."""
    roboto_40 = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=40)
    """The Roboto font with a size of 40."""

    roboto = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=28)
    """The Roboto font with a size of 28."""

    roboto_small = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=18)
    """The Roboto font with a smaller size of 18."""

    roboto_small2 = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=15)
    """The Roboto font with an even smaller size of 15."""

    point = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=100)
    """The Roboto font with a large size of 100."""

    roboro_icon = ImageFont.truetype('res/fonts/Roboto-icons.ttf', size=28)


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
            'kills_per_battle': (150, 712),
            'damage_ratio': (150, 865),
            'destruction_ratio': (150, 1010),
            'average_spotted': (150, 1160),

            'shots': (350, 712),
            'damage_caused': (350, 865),
            'enemies_destroyed': (350, 1010),
            'battles_survived': (350, 1160),

            'all_xp': (553, 712),
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
        if round(val, 2) == val == 0:
            if not enable_null:
                return '—'
            else:
                return '0'

        return '{:.2f}'.format(val)

    @staticmethod
    def other(val, enable_null=False):
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


class Colors():
    """
    A class that represents different colors.
    """
    blue = (0, 136, 252)     # Represents the color blue
    yellow = (255, 252, 0)   # Represents the color yellow
    red = (192, 21, 21)      # Represents the color red
    purple = (116, 30, 169)  # Represents the color purple
    orange = (205, 106, 29)  # Represents the color orange
    green = (30, 255, 38)    # Represents the color green
    cyan = (30, 187, 169)    # Represents the color cyan
    grey = (121, 121, 121)   # Represents the color grey
    l_grey = (200, 200, 200) # Represents the color light grey


@singleton
class ImageGen():
    text = None
    fonts = Fonts()
    leagues = Leagues()
    cache = FIFOCache(maxsize=100, ttl=60)
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

    def generate(self,
                ctx: Context | None,
                data: PlayerGlobalData, 
                speed_test: bool = False, 
                disable_cache: bool = False,
                debug_label: bool = False,
                    ) -> BytesIO | float:
        
        default_bg = False
        self.text = Text().get()
        start_time = time()
        need_caching = False
        current_lang = Text().get_current_lang()
        pdb = PlayersDB()
        sdb = ServersDB()

        if speed_test:
            disable_cache = True

        cached_data = self.cache.get((str(data.id), current_lang))

        if disable_cache:
            cached_data = None
        if cached_data is None:
            need_caching = True
            _log.debug('Cache miss')
        else:
            _log.debug('Image loaded from cache')
            self.draw_cache_label(cached_data)
            bin_image = BytesIO()
            cached_data.save(bin_image, 'PNG')
            bin_image.seek(0)
            _log.debug(
                'Image was sent in %s sec.', 
                round(time() - start_time, 4)
                )
            return bin_image
        
        if ctx == None:
            default_bg = True

        bin_image = None
        self.data = data
        self.values = Values(data)
        self.stat_all = data.data.statistics.all
        self.stat_rating = data.data.statistics.rating
        self.achievements = data.data.achievements

        if not default_bg:
            if pdb.check_member_premium(ctx.author.id):
                if pdb.get_member_image(ctx.author.id) is not None:
                    image_bytes = base64.b64decode(pdb.get_member_image(ctx.author.id))
                    if image_bytes != None: 
                        image_buffer = BytesIO(image_bytes)
                        self.image = Image.open(image_buffer)
                        # self.image.resize((700, 1250), Image.Resampling.BICUBIC)
                        # self.image = self.image.convert('RGBA')
            
            elif sdb.check_server_premium(ctx.guild.id):
                if sdb.get_server_image(ctx.guild.id) is not None:
                    image_bytes = base64.b64decode(sdb.get_server_image(ctx.guild.id))
                    if image_bytes != None:   
                        image_buffer = BytesIO(image_bytes)
                        self.image = Image.open(image_buffer)
                        # self.image = self.image.resize((700, 1250), Image.Resampling.BICUBIC)
                        # self.image = self.image.convert('RGBA')
            else:
                self.image = Image.open('res/image/default_image/common_stats.png')
                default_bg = True
        else:
            self.image = Image.open('res/image/default_image/common_stats.png')
            default_bg = True

        self.img_size = self.image.size
        self.coord = Coordinates(self.img_size)
        img_draw = ImageDraw.Draw(self.image)

        _log.debug(f'Generate modele debug: image size: {self.image.size}')

        if not default_bg:
            self.darw_backround()
            self.draw_stats_icons()
            self.draw_medals()

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
        self.darw_common_stats(img_draw)
        self.darw_medal_count(img_draw)

        if debug_label:
            self.draw_debug_label(img_draw)

        # self.draw_main_points(img_draw)
        # self.draw_rating_points(img_draw)
        # self.darw_common_points(img_draw)

        if need_caching:
            self.cache.set((str(data.id), current_lang), self.image)
            _log.debug('Image added to cache')

        bin_image = BytesIO()
        self.image.save(bin_image, 'PNG')
        bin_image.seek(0)
        _log.debug('Image was sent in %s sec.', round(time() - start_time, 4))

        return bin_image if not speed_test else time() - start_time

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

    def darw_backround(self) -> None:
        background_map = Image.new(mode='RGBA', size=self.image.size, color=(0, 0, 0, 0))
        img_draw = ImageDraw.Draw(background_map)

        # draw nickanme rectangle
        text_box = img_draw.textbbox(
            (self.img_size[0]//2, 20),
            text=self.data.data.name_and_tag,
            font=self.fonts.roboro_icon,
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

        # draw stats rectangles
        img_draw.rounded_rectangle(self.background_rectangles_map.main, radius=30, fill=(0, 0, 0))
        img_draw.rounded_rectangle(self.background_rectangles_map.rating, radius=30, fill=(0, 0, 0))
        img_draw.rounded_rectangle(self.background_rectangles_map.medals, radius=30, fill=(0, 0, 0))
        img_draw.rounded_rectangle(self.background_rectangles_map.total, radius=30, fill=(0, 0, 0))

        bg = self.image.copy()
        gaussian_filter = ImageFilter.GaussianBlur(radius=5)

        bg = bg.filter(gaussian_filter)
        bg = ImageEnhance.Brightness(bg).enhance(0)

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


    def draw_nickname(self, img: Image.Image):
        img.text(
            (self.img_size[0]//2, 20),
            text=self.data.data.name_and_tag,
            font=self.fonts.roboro_icon,
            anchor='ma',
            fill=Colors.blue)
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
                fill=Colors.blue
            )

    def draw_medals_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.medals_labels.keys():
            img.text(
                self.coord.medals_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small2,
                anchor='ma',
                align='center',
                fill=Colors.blue
            )

    def draw_common_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.common_stats_labels.keys():
            img.text(
                self.coord.common_stats_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small2,
                anchor='ma',
                align='center',
                fill=Colors.blue
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
                fill=Colors.blue
            )

    def draw_rating_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.rating_labels.keys():
            img.text(
                self.coord.rating_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small2,
                anchor='ma',
                align='center',
                fill=Colors.blue
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
        elif rating > 5000:
            text = self.text.for_image.leagues.brilliant
        else:
            text = self.text.for_image.leagues.no_league

        img.text(
            self.coord.rating_league_label,
            text=text,
            font=self.fonts.roboto_small2,
            anchor='ma',
            # align='center',
            fill=Colors.blue
        )

    def draw_main_stats(self, img: Image.Image):
        for i in self.coord.main_stats.keys():
            img.text(
                self.coord.main_stats[i],
                text=self.values.main[i],
                font=self.fonts.roboto,
                anchor='mm',
            )

    def draw_rating_stats(self, img: Image.Image):
        for i in self.coord.rating_stats.keys():
            img.text(
                self.coord.rating_stats[i],
                text=self.values.rating[i],
                font=self.fonts.roboto,
                anchor='ma',
            )

    def darw_common_stats(self, img: Image.Image):
        for i in self.coord.common_stats.keys():
            img.text(
                self.coord.common_stats[i],
                text=self.values.common[i],
                font=self.fonts.roboto,
                anchor='ma',
            )

    def darw_medal_count(self, img: Image.Image):
        for i in self.coord.medals_count.keys():
            img.text(
                self.coord.medals_count[i],
                text=str(getattr(self.achievements, i)),
                font=self.fonts.roboto_small2,
                anchor='ma',
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

    def draw_rating_points(self, img: Image.Image):
        for i in self.coord.rating_stats_point.keys():
            img.text(
                self.coord.rating_stats_point[i],
                text='.',
                font=self.fonts.point,
                anchor='mm',
                fill=self.point_coloring(i, getattr(
                    self.data.data.statistics.rating, i), rating=True)
            )

    def darw_common_points(self, img: Image.Image):
        for i in self.coord.common_stats_point.keys():
            img.text(
                self.coord.common_stats_point[i],
                text='.',
                font=self.fonts.point,
                anchor='mm',
                fill=self.point_coloring(
                    i, getattr(self.data.data.statistics.all, i), rating=True)
            )

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

    def point_coloring(self, stats_type, stats_value, rating=False):
        val = stats_value
        if stats_type == 'winrate':
            if val == 0:
                return Colors.grey
            if val <= 44:
                return Colors.red
            if val <= 47:
                return Colors.orange
            if val <= 50:
                return Colors.yellow
            if val <= 55:
                return Colors.green
            if val < 60:
                return Colors.cyan
            if val >= 60:
                return Colors.purple

        elif stats_type == 'avg_damage':
            if val == 0:
                return Colors.grey
            if val < 600:
                return Colors.red
            if val < 900:
                return Colors.orange
            if val < 1200:
                return Colors.yellow
            if val < 1700:
                return Colors.green
            if val < 2500:
                return Colors.cyan
            if val >= 2500:
                return Colors.purple

        elif stats_type == 'battles':
            if val == 0:
                return Colors.grey
            if val < 2000:
                return Colors.red
            if val < 5000:
                return Colors.orange
            if val < 10000:
                return Colors.yellow
            if val < 30000:
                return Colors.green
            if val < 50000:
                return Colors.cyan
            if val >= 50000:
                return Colors.purple

        elif stats_type == 'battles' and rating:
            if val == 0:
                return Colors.grey
            if val < 300:
                return Colors.red
            if val < 700:
                return Colors.orange
            if val < 1000:
                return Colors.yellow
            if val < 3000:
                return Colors.green
            if val < 6000:
                return Colors.cyan
            if val >= 6000:
                return Colors.purple

        elif stats_type == 'frags_per_battle':
            if val == 0:
                return Colors.grey
            if val < 0.60:
                return Colors.red
            if val < 0.75:
                return Colors.orange
            if val < 1:
                return Colors.yellow
            if val < 1.2:
                return Colors.green
            if val < 1.3:
                return Colors.cyan
            if val >= 1.3:
                return Colors.purple

        elif stats_type == 'damage_ratio':
            if val == 0:
                return Colors.grey
            if val < 0.7:
                return Colors.red
            if val < 0.9:
                return Colors.orange
            if val < 1:
                return Colors.yellow
            if val < 1.3:
                return Colors.green
            if val < 2:
                return Colors.cyan
            if val >= 2:
                return Colors.purple

        elif stats_type == 'destruction_ratio':
            if val == 0:
                return Colors.grey
            if val < 0.6:
                return Colors.red
            if val < 0.8:
                return Colors.orange
            if val < 1:
                return Colors.yellow
            if val < 1.4:
                return Colors.green
            if val < 2.4:
                return Colors.cyan
            if val >= 2.4:
                return Colors.purple

        elif stats_type == 'avg_spotted':
            if val == 0:
                return Colors.grey
            if val < 0.7:
                return Colors.red
            if val < 0.9:
                return Colors.orange
            if val < 1:
                return Colors.yellow
            if val < 1.2:
                return Colors.green
            if val < 1.5:
                return Colors.cyan
            if val >= 1.5:
                return Colors.purple

        elif stats_type == 'accuracy':
            if val == 0:
                return Colors.grey
            if val < 60:
                return Colors.red
            if val < 65:
                return Colors.orange
            if val < 70:
                return Colors.yellow
            if val < 75:
                return Colors.green
            if val < 85:
                return Colors.cyan
            if val >= 85:
                return Colors.purple
            
    async def speed_test(self):
        try:
            data, response_time = await async_wotb_api.test('rtx4080', 'eu', speed_test=True)
        except:
            return (0, 0)
        generate_time = self.generate(ctx=None, data=data, speed_test=True)
        return(
            round(response_time, 3),
            round(generate_time, 3)
        )

    async def test(self):
        import lib.api.async_wotb_api as async_wotb_api
        player_data = await async_wotb_api.test('rtx4080', 'eu')
        self.generate(ctx=None, data=player_data[0], disable_cache=True, debug_label=False)
        self.image.show()
        quit()

