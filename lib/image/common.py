'''
Модуль для генерирования изображения
со статистикой.
'''
if __name__ == '__main__':

    import os
    import sys
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    sys.path.insert(0, path)

from datetime import datetime
from io import BytesIO
from time import time

from PIL import Image, ImageDraw, ImageFont

from lib.data_classes.api_data import PlayerGlobalData
from lib.locale.locale import Text
from lib.logger import logger
from lib.utils.singleton_factory import singleton

_log = logger.get_logger(__name__, 'ImageCommonLogger',
                         'logs/image_common.log')


class ImageCache():
    cache: dict = {}
    cache_ttl: int = 60  # seconds
    cache_size: int = 40  # items

    def check_item(self, key):
        if key in self.cache.keys():
            return True
        return False

    def _overflow_handler(self):
        overflow = len(self.cache.keys()) - self.cache_size
        if overflow > 0:
            for i in range(overflow):
                key = list(self.cache.keys())[i]
                self.cache.pop(key)

    def del_item(self, key):
        del self.cache[key]

    def check_timestamp(self, key):
        current_time = datetime.now().timestamp()
        time_stamp = self.cache[key]['timestamp']
        time_delta = current_time - time_stamp
        if time_delta > self.cache_ttl:
            del self.cache[key]
            return False
        else:
            return True

    def add_item(self, item):
        self._overflow_handler()
        self.cache[item['id']] = item

    def get_item(self, key):
        if self.check_item(key):
            if self.check_timestamp(key):
                return self.cache[key]

        raise KeyError('Cache miss')


class Fonts():
    roboto = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=28)
    roboto_small = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=18)
    roboto_small2 = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=15)
    point = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=100)


class Leagues():
    empty = Image.open('res/image/leagues/no-rating.png', formats=['png'])
    gold = Image.open('res/image/leagues/gold.png', formats=['png'])
    platinum = Image.open('res/image/leagues/platinum.png', formats=['png'])
    brilliant = Image.open('res/image/leagues/brilliant.png', formats=['png'])
    calibration = Image.open('res/image/leagues/calibr.png', formats=['png'])


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
            'mainGun': (143, 360),
            'medalRadleyWalters': (242, 360),
            'markOfMastery': (350, 360),
            'medalKolobanov': (458, 360),
            'warrior': (560, 360),
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

            'all_xp': (550, 712),
            'max_xp': (550, 865),
            'max_frags': (550, 1010),
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
            'rating_battles': (150, 535),
            'winrate': (553, 535),
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

            'xp': (550, 680),
            'max_xp': (550, 832),
            'max_frags': (550, 976),
            'accuracy': (550, 1125),
        }
        self.medals_count = {
            'mainGun': (143, 344),
            'medalRadleyWalters': (242, 344),
            'markOfMastery': (350, 344),
            'medalKolobanov': (458, 344),
            'warrior': (560, 344),
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
    def winrate(val):
        if val == 0:
            return '—'

        return '{:.2f}'.format(val) + ' %'

    @staticmethod
    def ratio(val):
        if val == 0:
            return '—'

        return '{:.2f}'.format(val)

    @staticmethod
    def other(val):
        if val == 0:
            return '—'

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
            'winrate': self.val_normalizer.other(shorted_data.rating.battles),
            'rating': self.val_normalizer.other(shorted_data.rating.rating),
            'battles': self.val_normalizer.winrate(shorted_data.rating.winrate)
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
    blue = (0, 136, 252)
    yellow = (255, 252, 0)
    red = (192, 21, 21)
    purple = (116, 30, 169)
    orange = (205, 106, 29)
    green = (30, 255, 38)
    cyan = (30, 187, 169)
    grey = (121, 121, 121)


@singleton
class ImageGen():
    text = None
    fonts = Fonts()
    colors = Colors()
    leagues = Leagues()
    cache = ImageCache()
    value = None
    data = None
    diff_data = None
    image = None
    stat_all = None
    stat_rating = None
    achievements = None
    img_size = []
    coord = None

    def generate(self, data: PlayerGlobalData):
        self.text = Text().get()
        start_time = time()
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
                       round(time() - start_time, 4))
            return bin_image

        bin_image = None
        self.data = data
        self.values = Values(data)
        self.stat_all = data.data.statistics.all
        self.stat_rating = data.data.statistics.rating
        self.achievements = data.data.achievements

        self.image = Image.open('res/image/default_image/common_stats.png')
        self.img_size = self.image.size
        self.coord = Coordinates(self.img_size)

        img_draw = ImageDraw.Draw(self.image)
        self.draw_category_labels(img_draw)
        self.draw_medals_labels(img_draw)
        self.draw_common_labels(img_draw)
        self.draw_rating_labels(img_draw)
        self.draw_main_labels(img_draw)
        self.draw_rating_icon()
        self.draw_nickname(img_draw)

        self.draw_main_stats(img_draw)
        self.draw_rating_stats(img_draw)
        self.darw_common_stats(img_draw)
        self.darw_medal_count(img_draw)

        # self.draw_main_points(img_draw)
        # self.draw_rating_points(img_draw)
        # self.darw_common_points(img_draw)

        return_data = {'img': self.image, 'timestamp': datetime.now(
        ).timestamp(), 'id': str(data.id)}

        if need_caching:
            self.cache.add_item(return_data)
            _log.debug('Image added to cache')

        bin_image = BytesIO()
        self.image.save(bin_image, 'PNG')
        bin_image.seek(0)
        _log.debug('Image was sent in %s sec.', round(time() - start_time, 4))

        return bin_image

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
            font=self.fonts.roboto,
            anchor='ma',
            fill=self.colors.blue)
        img.text(
            (self.img_size[0]//2, 55),
            text=f'ID: {str(self.data.id)}',
            font=self.fonts.roboto_small2,
            anchor='ma',
            fill=self.colors.grey)

    def draw_category_labels(self, img: object):
        for i in self.coord.category_labels.keys():
            img.text(
                self.coord.category_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small,
                anchor='mm',
                fill=self.colors.blue
            )

    def draw_medals_labels(self, img: object):
        for i in self.coord.medals_labels.keys():
            img.text(
                self.coord.medals_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small2,
                anchor='ma',
                align='center',
                fill=self.colors.blue
            )

    def draw_common_labels(self, img: object):
        for i in self.coord.common_stats_labels.keys():
            img.text(
                self.coord.common_stats_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small2,
                anchor='ma',
                align='center',
                fill=self.colors.blue
            )

    def draw_main_labels(self, img: object):
        for i in self.coord.main_labels.keys():
            img.text(
                self.coord.main_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small2,
                anchor='ma',
                align='center',
                fill=self.colors.blue
            )

    def draw_rating_labels(self, img: object):
        for i in self.coord.rating_labels.keys():
            img.text(
                self.coord.rating_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small2,
                anchor='ma',
                align='center',
                fill=self.colors.blue
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
            fill=self.colors.blue
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
                fill=self.point_coloring(i, getattr(self.data.all, i))
            )

    def draw_rating_points(self, img: Image.Image):
        for i in self.coord.main_stats_points.keys():
            img.text(
                self.coord.main_stats_points[i],
                text='.',
                font=self.fonts.point,
                anchor='mm',
                fill=self.point_coloring(i, getattr(self.data.all, i))
            )

    def draw_rating_points(self, img: Image.Image):
        for i in self.coord.rating_stats_point.keys():
            img.text(
                self.coord.rating_stats_point[i],
                text='.',
                font=self.fonts.point,
                anchor='mm',
                fill=self.point_coloring(i, getattr(
                    self.data.rating, i), rating=True)
            )

    def darw_common_points(self, img: Image.Image):
        for i in self.coord.common_stats_point.keys():
            img.text(
                self.coord.common_stats_point[i],
                text='.',
                font=self.fonts.point,
                anchor='mm',
                fill=self.point_coloring(
                    i, getattr(self.data.all, i), rating=True)
            )

    def point_coloring(self, stats_type, stats_value, rating=False):
        val = stats_value
        if stats_type == 'winrate':
            if val == 0:
                return self.colors.grey
            if val <= 44:
                return self.colors.red
            if val <= 47:
                return self.colors.orange
            if val <= 50:
                return self.colors.yellow
            if val <= 55:
                return self.colors.green
            if val < 60:
                return self.colors.cyan
            if val >= 60:
                return self.colors.purple

        elif stats_type == 'avg_damage':
            if val == 0:
                return self.colors.grey
            if val < 600:
                return self.colors.red
            if val < 900:
                return self.colors.orange
            if val < 1200:
                return self.colors.yellow
            if val < 1700:
                return self.colors.green
            if val < 2500:
                return self.colors.cyan
            if val >= 2500:
                return self.colors.purple

        elif stats_type == 'battles':
            if val == 0:
                return self.colors.grey
            if val < 2000:
                return self.colors.red
            if val < 5000:
                return self.colors.orange
            if val < 10000:
                return self.colors.yellow
            if val < 30000:
                return self.colors.green
            if val < 50000:
                return self.colors.cyan
            if val >= 50000:
                return self.colors.purple

        elif stats_type == 'battles' and rating:
            if val == 0:
                return self.colors.grey
            if val < 300:
                return self.colors.red
            if val < 700:
                return self.colors.orange
            if val < 1000:
                return self.colors.yellow
            if val < 3000:
                return self.colors.green
            if val < 6000:
                return self.colors.cyan
            if val >= 6000:
                return self.colors.purple

        elif stats_type == 'frags_per_battle':
            if val == 0:
                return self.colors.grey
            if val < 0.60:
                return self.colors.red
            if val < 0.75:
                return self.colors.orange
            if val < 1:
                return self.colors.yellow
            if val < 1.2:
                return self.colors.green
            if val < 1.3:
                return self.colors.cyan
            if val >= 1.3:
                return self.colors.purple

        elif stats_type == 'damage_ratio':
            if val == 0:
                return self.colors.grey
            if val < 0.7:
                return self.colors.red
            if val < 0.9:
                return self.colors.orange
            if val < 1:
                return self.colors.yellow
            if val < 1.3:
                return self.colors.green
            if val < 2:
                return self.colors.cyan
            if val >= 2:
                return self.colors.purple

        elif stats_type == 'destruction_ratio':
            if val == 0:
                return self.colors.grey
            if val < 0.6:
                return self.colors.red
            if val < 0.8:
                return self.colors.orange
            if val < 1:
                return self.colors.yellow
            if val < 1.4:
                return self.colors.green
            if val < 2.4:
                return self.colors.cyan
            if val >= 2.4:
                return self.colors.purple

        elif stats_type == 'avg_spotted':
            if val == 0:
                return self.colors.grey
            if val < 0.7:
                return self.colors.red
            if val < 0.9:
                return self.colors.orange
            if val < 1:
                return self.colors.yellow
            if val < 1.2:
                return self.colors.green
            if val < 1.5:
                return self.colors.cyan
            if val >= 1.5:
                return self.colors.purple

        elif stats_type == 'accuracy':
            if val == 0:
                return self.colors.grey
            if val < 60:
                return self.colors.red
            if val < 65:
                return self.colors.orange
            if val < 70:
                return self.colors.yellow
            if val < 75:
                return self.colors.green
            if val < 85:
                return self.colors.cyan
            if val >= 85:
                return self.colors.purple

    def test(self):
        import api.async_wotb_api as async_wotb_api
        self.generate_session(async_wotb_api.test('L3oN1_'), )
        self.image.show()
        self.image.close()
        quit()

# ImageGen().test()
