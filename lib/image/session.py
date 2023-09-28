import json
from datetime import datetime
from io import BytesIO
from time import time

if __name__ == '__main__':
    import os
    import sys
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    sys.path.insert(0, path)
    from lib.yaml.yaml2object import Parser

from PIL import Image, ImageDraw, ImageFont

from lib.exceptions.database import TankNotFoundInTankopedia
from lib.data_classes.api_data import PlayerGlobalData
from lib.data_classes.session import SesionDiffData
from lib.database.players import PlayersDB
from lib.database.tankopedia import TanksDB
from lib.image.common import Colors, Fonts, ValueNormalizer
from lib.locale.locale import Text
from lib.logger import logger
from lib.utils.singleton_factory import singleton

_log = logger.get_logger(__name__, 'ImageSessionLogger',
                         'logs/image_session.log')


from typing import Dict

class ImageCache():
    """
    A class that represents an image cache.
    """

    cache: Dict[str, dict] = {}
    cache_ttl: int = 60  # seconds
    cache_size: int = 40  # items

    def check_item(self, key: str) -> bool:
        """
        Check if an item exists in the cache.

        Args:
            key: The key to check.

        Returns:
            True if the item exists in the cache, False otherwise.
        """
        if key in self.cache.keys():
            return True
        return False

    def _overflow_handler(self) -> None:
        """
        Handle cache overflow by removing oldest items from the cache.
        """
        overflow = len(self.cache.keys()) - self.cache_size
        if overflow > 0:
            for i in range(overflow):
                key = list(self.cache.keys())[i]
                self.cache.pop(key)

    def del_item(self, key: str) -> None:
        """
        Delete an item from the cache.

        Args:
            key: The key of the item to delete.
        """
        del self.cache[key]

    def check_timestamp(self, key: str) -> bool:
        """
        Check if an item in the cache has expired based on its timestamp.

        Args:
            key: The key of the item to check.

        Returns:
            True if the item has not expired, False otherwise.
        """
        current_time = datetime.now().timestamp()
        time_stamp = self.cache[key]['timestamp']
        time_delta = current_time - time_stamp
        if time_delta > self.cache_ttl:
            del self.cache[key]
            return False
        else:
            return True

    def add_item(self, item: dict) -> None:
        """
        Add an item to the cache, handling cache overflow if necessary.

        Args:
            item: The item to add to the cache.
        """
        self._overflow_handler()
        self.cache[item['id']] = item

    def get_item(self, key: str) -> dict:
        """
        Get an item from the cache.

        Args:
            key: The key of the item to get.

        Returns:
            The item from the cache.

        Raises:
            KeyError: If the item does not exist in the cache or has expired.
        """
        if self.check_item(key):
            if self.check_timestamp(key):
                return self.cache[key]

        raise KeyError('Cache miss')


class Fonts():
    """A class that holds different font styles for the images."""

    roboto = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=28)  # Roboto font with size 28
    roboto_25 = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=25)  # Roboto font with size 25
    roboto_medium = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=22)  # Roboto font with size 22
    roboto_small = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=18)  # Roboto font with size 18
    roboto_small2 = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=15)  # Roboto font with size 15
    roboto_icons = ImageFont.truetype('res/fonts/Roboto-icons.ttf', size=22)  # Roboto font with size 28
    point = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=100)  # Roboto font with size 100


class Leagues():
    """A class that holds different league images."""

    empty = Image.open('res/image/leagues/no-rating.png', formats=['png'])  # Empty league image
    gold = Image.open('res/image/leagues/gold.png', formats=['png'])  # Gold league image
    platinum = Image.open('res/image/leagues/platinum.png', formats=['png'])  # Platinum league image
    brilliant = Image.open('res/image/leagues/brilliant.png', formats=['png'])  # Brilliant league image
    calibration = Image.open('res/image/leagues/calibr.png', formats=['png'])  # Calibration league image


class Coordinates():
    def __init__(self, img_size):
        """
        Class to store coordinates for labels and stats in an image.

        Args:
        - img_size (tuple): Size of the image (width, height)
        """
        _center_x = img_size[0] // 2

        # Category labels
        self.category_labels = {
            'main': (_center_x, 100),  # Main category label
            'rating': (_center_x, 360)  # Rating category label
        }

        # Main labels
        self.main_labels = {
            'winrate': (150, 275),  # Winrate label
            'avg_damage': (_center_x, 275),  # Average damage label
            'battles': (553, 275),  # Battles label
        }

        # Main stats
        self.main_stats = {
            'winrate': (150, 165),  # Winrate stat
            'avg_damage': (_center_x, 165),  # Average damage stat
            'battles': (553, 165),  # Battles stat
        }

        # Main difference stats
        self.main_diff_stats = {
            'winrate': (150, 240),  # Winrate difference stat
            'avg_damage': (_center_x, 240),  # Average damage difference stat
            'battles': (553, 240),  # Battles difference stat
        }

        # Main session stats
        self.main_session_stats = {
            'winrate': (150, 205),  # Winrate session stat
            'avg_damage': (_center_x, 205),  # Average damage session stat
            'battles': (553, 205),  # Battles session stat
        }

        # Rating labels
        self.rating_labels = {
            'rating_battles': (150, 560),  # Rating battles label
            'winrate': (553, 560),  # Winrate label
        }

        # Rating league label
        self.rating_league_label = _center_x, 560,

        # Rating league icon
        self.rating_league_icon = _center_x - Leagues.empty.size[0]//2, 380,

        # Rating stats
        self.rating_stats = {
            'winrate': (150, 425),  # Winrate stat
            'rating': (_center_x, 440),  # Rating stat
            'battles': (553, 425),  # Battles stat
        }

        # Ratings session stats
        self.rating_session_stats = {
            'winrate': (150, 480),  # Winrate session stat
            'rating': (_center_x, 480),  # Rating session stat
            'battles': (553, 480),  # Battles session stat
        }

        # Rating difference stats
        self.rating_diff_stats = {
            'winrate': (150, 520),  # Winrate difference stat
            'rating': (_center_x, 520),  # Rating difference stat
            'battles': (553, 520),  # Battles difference stat
        }

        # Tank name
        self.tank_name = (_center_x, 630)

        # Tank stats
        self.tank_stats = {
            'winrate': (150, 710),  # Winrate stat
            'avg_damage': (_center_x, 710),  # Average damage stat
            'battles': (553, 710)  # Battles stat
        }

        # Tank difference stats
        self.tank_diff_stats = {
            'winrate': (150, 795),  # Winrate difference stat
            'avg_damage': (_center_x, 795),  # Average damage difference stat
            'battles': (553, 795)  # Battles difference stat
        }

        # Tank session stats
        self.tank_session_stats = {
            'winrate': (150, 755),  # Winrate session stat
            'avg_damage': (_center_x, 755),  # Average damage session stat
            'battles': (553, 755)  # Battles session stat
        }

        # Tank labels
        self.tank_labels = {
            'winrate': (150, 830),  # Winrate label
            'avg_damage': (_center_x, 830),  # Average damage label
            'battles': (553, 830)  # Battles label
        }


class DiffValues():
    def __init__(self, diff_data: SesionDiffData) -> None:
        """
        Initializes a DiffValues object with the given diff_data.

        Args:
            diff_data (SesionDiffData): The diff_data object containing the differences.

        Returns:
            None
        """
        self.val_normalizer = ValueNormalizer()
        self.main = {
            'winrate': self.value_colors(diff_data.main_diff.winrate) + self.val_normalizer.winrate(diff_data.main_diff.winrate),
            'avg_damage': self.value_colors(diff_data.main_diff.avg_damage) + self.val_normalizer.other(diff_data.main_diff.avg_damage),
            'battles': self.value_colors(diff_data.main_diff.battles) + self.val_normalizer.other(diff_data.main_diff.battles)
        }
        self.rating = {
            'winrate': self.value_colors(diff_data.rating_diff.winrate) + self.val_normalizer.winrate(diff_data.rating_diff.winrate),
            'rating': self.value_colors(diff_data.rating_diff.rating) + self.val_normalizer.other(diff_data.rating_diff.rating),
            'battles': self.value_colors(diff_data.rating_diff.battles) + self.val_normalizer.other(diff_data.rating_diff.battles)
        }
        self.tank = {
            'winrate': self.value_colors(diff_data.tank_diff.winrate) + self.val_normalizer.winrate(diff_data.tank_diff.winrate),
            'avg_damage': self.value_colors(diff_data.tank_diff.avg_damage) + self.val_normalizer.other(diff_data.tank_diff.avg_damage),
            'battles': self.value_colors(diff_data.tank_diff.battles) + self.val_normalizer.other(diff_data.tank_diff.battles)
        }

    def value_colors(self, value: int | float) -> str:
        if value > 0:
            return '+'
        else:
            return ''

class SessionValues():
    def __init__(self, session_data: SesionDiffData) -> None:
        self.val_normalizer = ValueNormalizer()
        self.main = {
            'winrate': self.val_normalizer.winrate(session_data.main_session.winrate, True),
            'avg_damage': self.val_normalizer.other(session_data.main_session.avg_damage, True),
            'battles': self.val_normalizer.other(session_data.main_session.battles, True)
        }

        self.rating = {
            'winrate': self.val_normalizer.winrate(session_data.rating_session.winrate, True),
            'rating': self.val_normalizer.other(session_data.rating_session.rating, True),
            'battles': self.val_normalizer.other(session_data.rating_session.battles, True)
        }

        self.tank = {
            'winrate': self.val_normalizer.winrate(session_data.tank_session.winrate, True),
            'avg_damage': self.val_normalizer.other(session_data.tank_session.avg_damage, True),
            'battles': self.val_normalizer.other(session_data.tank_session.battles, True)
        }


class Values():
    def __init__(self, data: PlayerGlobalData, tank_index: int) -> None:
        """
        Initializes a Values object.

        Args:
            data (PlayerGlobalData): The player's global data.
            tank_index (int): The index of the tank in the tankopedia_db list.
        """
        self.val_normalizer = ValueNormalizer()
        stats_data = data.data.statistics
        tank_data = data.data.tank_stats

        # Define the main statistics
        self.main = {
            'winrate': self.val_normalizer.winrate(stats_data.all.winrate),
            'avg_damage': self.val_normalizer.other(stats_data.all.avg_damage),
            'battles': self.val_normalizer.other(stats_data.all.battles)
        }

        # Define the rating statistics
        self.rating = {
            'winrate': self.val_normalizer.winrate(stats_data.rating.winrate),
            'rating': self.val_normalizer.other(stats_data.rating.rating),
            'battles': self.val_normalizer.other(stats_data.rating.battles)
        }

        # Define the tank statistics
        self.tank = {
            'winrate': self.val_normalizer.winrate(tank_data[tank_index].all.winrate),
            'avg_damage': self.val_normalizer.other(tank_data[tank_index].all.avg_damage),
            'battles': self.val_normalizer.other(tank_data[tank_index].all.battles)
        }


class Flags():
    eu = Image.open('res/image/flags/eu.png', formats=['png'])
    ruby = Image.open('res/image/flags/ruby.png', formats=['png'])
    usa = Image.open('res/image/flags/usa.png', formats=['png'])
    china = Image.open('res/image/flags/china.png', formats=['png'])


@singleton
class ImageGen():
    cache = ImageCache()
    colors = Colors()
    fonts = Fonts()
    session_values = None
    diff_values = None
    diff_data = None
    img_size = None
    leagues = None
    values = None
    coord = None
    image = None
    data = None
    text = None

    def generate(self, data: PlayerGlobalData, diff_data: SesionDiffData, test = False):
        """
        Generate the image for the given player's session stats.

        Args:
            test (bool): If True, the image will be displayed for testing purposes.
            data (PlayerGlobalData): The global data of the player.
            diff_data (SesionDiffData): The diff data of the session.

        Returns:
            BytesIO: The image generated for the session stats.
        """
        self.diff_data = diff_data
        self.data = data
        self.diff_values = DiffValues(diff_data)
        self.session_values = SessionValues(diff_data)
        self.values = Values(data, self.diff_data.tank_index)

        tank_type = TanksDB().get_tank_by_id(str(self.diff_data.tank_id))['type']
        tank_tier = TanksDB().get_tank_by_id(str(self.diff_data.tank_id))['tier']

        try:
            self.curr_tank_name = self.tank_type_handler(tank_type) + TanksDB().get_tank_by_id(
                str(self.diff_data.tank_id))['name'] + self.tank_tier_handler(tank_tier)
        except TankNotFoundInTankopedia:
            self.curr_tank_name = 'Unknown'

        strt_time = time()
        self.leagues = Leagues()
        need_caching = False

        try:
            cached_data = self.cache.get_item(str(data.id))
        except KeyError:
            need_caching = True
            _log.debug('Cache miss')
        else:
            _log.debug('Image loaded from cache')
            bin_image = None
            bin_image = BytesIO()
            cached_data['img'].save(bin_image, 'PNG')
            bin_image.seek(0)
            _log.debug('Image was sent in %s sec.',
                       round(time() - strt_time, 4))
            return bin_image

        self.text = Text().get()
        self.image = Image.open('res/image/default_image/session_stats.png')
        self.img_size = self.image.size
        self.coord = Coordinates(self.img_size)

        img_draw = ImageDraw.Draw(self.image)
        self.draw_nickname(img_draw)
        self.draw_category_labels(img_draw)

        self.draw_main_labels(img_draw)

        self.draw_rating_labels(img_draw)
        self.draw_rating_diff_stats(img_draw)

        self.draw_rating_stats(img_draw)
        self.draw_rating_icon(img_draw)
        self.draw_rating_session_stats(img_draw)

        self.draw_main_stats(img_draw)
        self.draw_main_diff_stats(img_draw)
        self.draw_main_session_stats(img_draw)

        self.draw_tank_name(img_draw)
        self.draw_tank_stats(img_draw)
        self.draw_tank_diff_stats(img_draw)
        self.draw_tank_session_stats(img_draw)
        self.draw_tank_labels(img_draw)

        return_data = {'img': self.image, 'timestamp': datetime.now(
        ).timestamp(), 'id': str(data.id)}

        if test:
            self.image.show()

        if need_caching:
            self.cache.add_item(return_data)
            _log.debug('Image added to cache')

        bin_image = BytesIO()
        self.image.save(bin_image, 'PNG')
        bin_image.seek(0)
        _log.debug('Image was sent in %s sec.', round(time() - strt_time, 4))

        return bin_image
    
    def tank_type_handler(self, tank_type: str):
        match tank_type:
            case 'heavyTank':
                return 'ﬄ • '
            case 'mediumTank':
                return 'ﬃ • '
            case 'lightTank':
                return 'ﬂ • '
            case 'AT-SPG':
                return 'ﬁ • '
            case _:
                _log.error(f'Ignoring Exception: Invalid tank type: {tank_type}')
                return '� • ' 
            
    def tank_tier_handler(self, tier: int):
        match tier:
            case 1:
                return ' • I'
            case 2:
                return ' • II'
            case 3:
                return ' • III'
            case 4:
                return ' • IV'
            case 5:
                return ' • V'
            case 6:
                return ' • VI'
            case 7:
                return ' • VII'
            case 8:
                return ' • VIII'
            case 9:
                return ' • IX'
            case 10:
                return ' • X'
            case _:
                _log.error(f'Ignoring Exception: Invalid tank tier: {tier}')
                return ' • ?'

    def draw_nickname(self, img: ImageDraw.ImageDraw):
        img.text(
            (self.img_size[0]//2, 20),
            text=self.data.data.name_and_tag,
            font=self.fonts.roboto,
            anchor='ma',
            fill=self.colors.blue)
        img.text(
            (self.img_size[0]//2, 55),
            text=f'ID: {str(self.data.id)}',
            font=self.fonts.roboto_small2,
            anchor='ma',
            fill=self.colors.l_grey)

    def draw_category_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.category_labels.keys():
            img.text(
                self.coord.category_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small,
                anchor='mm',
                fill=self.colors.blue
            )

    def draw_main_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.main_labels.keys():
            img.text(
                self.coord.main_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small,
                anchor='ma',
                align='center',
                fill=self.colors.blue
            )

    def draw_main_stats(self, img: ImageDraw.ImageDraw):
        for i in self.coord.main_stats.keys():
            img.text(
                self.coord.main_stats[i],
                text=self.values.main[i],
                font=self.fonts.roboto,
                anchor='ma',
                align='center',)

    def draw_main_diff_stats(self, img: ImageDraw.ImageDraw):
        for i in self.coord.main_diff_stats.keys():
            img.text(
                self.coord.main_diff_stats[i],
                text=self.diff_values.main[i],
                font=self.fonts.roboto_medium,
                anchor='ma',
                align='center',
                fill=self.value_colors(getattr(self.diff_data.main_diff, i))
            )
    
    def draw_main_session_stats(self, img: ImageDraw.ImageDraw):
        for i in self.coord.main_session_stats.keys():
            img.text(
                self.coord.main_session_stats[i],
                text=self.session_values.main[i],
                font=self.fonts.roboto_25,
                anchor='ma',
                align='center',
                fill=self.colors.l_grey)

    def draw_tank_name(self, img: ImageDraw.ImageDraw):
        img.text(
            self.coord.tank_name,
            text=self.curr_tank_name,
            font=self.fonts.roboto_icons,
            anchor='ma',
            align='center',
            fill=Colors.blue
        )

    def draw_rating_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.rating_labels.keys():
            img.text(
                self.coord.rating_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small,
                anchor='ma',
                align='center',
                fill=self.colors.blue
            )
        self._rating_label_handler(img)

    def draw_rating_stats(self, img: ImageDraw.ImageDraw):
        for i in self.coord.rating_stats.keys():
            img.text(
                self.coord.rating_stats[i],
                text=self.values.rating[i],
                font=self.fonts.roboto,
                anchor='ma',
                align='center')
            
    def draw_rating_session_stats(self, img: ImageDraw.ImageDraw):
        for i in self.coord.rating_session_stats.keys():
            img.text(
                self.coord.rating_session_stats[i],
                text=self.session_values.rating[i],
                font=self.fonts.roboto_25,
                anchor='ma',
                align='center',
                fill=self.colors.l_grey)

    def draw_rating_icon(self, img: ImageDraw.ImageDraw) -> None:
        rt_img = self.leagues.empty
        rating = self.data.data.statistics.rating.rating
        calibration_left = self.data.data.statistics.rating.calibration_battles_left

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

        self.image.paste(rt_img, self.coord.rating_league_icon, rt_img)

    def draw_tank_labels(self, img: ImageDraw.ImageDraw):
        pass

    def _rating_label_handler(self, img: ImageDraw.ImageDraw):
        rating = self.data.data.statistics.rating.rating
        if self.data.data.statistics.rating.calibration_battles_left == 10:
            text = self.text.for_image.no_rating
        elif self.data.data.statistics.rating.calibration_battles_left > 0:
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
            font=self.fonts.roboto_small,
            anchor='ma',
            # align='center',
            fill=self.colors.blue
        )

    def draw_rating_diff_stats(self, img: ImageDraw.ImageDraw):
        for i in self.coord.rating_diff_stats.keys():
            img.text(
                self.coord.rating_diff_stats[i],
                text=self.diff_values.rating[i],
                font=self.fonts.roboto_medium,
                anchor='ma',
                align='center',
                fill=self.value_colors(getattr(self.diff_data.rating_diff, i))
            )
        self._rating_label_handler(img)

    def draw_tank_stats(self, img: ImageDraw.ImageDraw):
        for i in self.coord.tank_stats.keys():
            img.text(
                self.coord.tank_stats[i],
                text=self.values.tank[i],
                font=self.fonts.roboto,
                anchor='ma',
                align='center'
            )

    def draw_tank_diff_stats(self, img: ImageDraw.ImageDraw):
        for i in self.coord.tank_stats.keys():
            img.text(
                self.coord.tank_diff_stats[i],
                text=self.diff_values.tank[i],
                font=self.fonts.roboto_medium,
                anchor='ma',
                align='center',
                fill=self.value_colors(getattr(self.diff_data.tank_diff, i))
            )

    def draw_tank_session_stats(self, img: ImageDraw.ImageDraw):
        for i in self.coord.tank_session_stats.keys():
            img.text(
                self.coord.tank_session_stats[i],
                text=self.session_values.tank[i],
                font=self.fonts.roboto_25,
                anchor='ma',
                align='center',
                fill=self.colors.l_grey)

    def draw_tank_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.tank_labels.keys():
            img.text(
                self.coord.tank_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small,
                anchor='ma',
                align='center',
                fill=self.colors.blue
            )
    
    def draw_flag(self):
        # self.data.region = 'asia' - Only for test
        match self.data.region:
            case 'ru':
                self.image.paste(self.flags.ruby, (10, 10), self.flags.ruby)
            case 'eu':
                self.image.paste(self.flags.eu, (10, 10), self.flags.eu)
            case 'com':
                self.image.paste(self.flags.usa, (10, 10), self.flags.usa)
            case 'asia':
                self.image.paste(self.flags.china, (10, 10), self.flags.china)

    def value_colors(self, value: int | float) -> tuple:
        if type(value) is str:
            return self.colors.grey
        if value > 0:
            return self.colors.green
        if value < 0:
            return self.colors.red
        if value == 0:
            return self.colors.grey


if __name__ == '__main__':

    from lib.api.async_wotb_api import test
    from lib.data_parser import parse_data

    data = test('VegaS_202', region='eu')
    player_stats = PlayerGlobalData(PlayersDB().get_member_last_stats(683407510820225098))
    session_stats = parse_data.get_session_stats(player_stats, data)
    ImageGen().generate(data=data, diff_data=session_stats, test=True)
