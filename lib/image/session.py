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

_log = logger.get_logger(__name__, 'ImageSessionLogger', 'logs/image_session.log')


class ImageCache():
    cache: dict = {}
    cache_ttl: int = 60 # seconds
    cache_size: int = 40 # items
    
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
    roboto_medium = ImageFont.truetype('res/fonts/Roboto-Medium.ttf', size=22)
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
            'main' : (_center_x, 95),
            'rating' : (_center_x, 320)
        }
        self.main_labels = {
            'winrate' : (150, 230),
            'avg_damage' : (_center_x, 230),
            'battles' : (553, 230),
        }
        self.main_stats = {
            'winrate' : (150, 165),
            'avg_damage' : (_center_x, 165),
            'battles' : (553, 165),
        }
        self.main_diff_stats = {
            'winrate' : (150, 195),
            'avg_damage' : (_center_x, 195),
            'battles' : (553, 195),
        }
        self.rating_labels = {
            'rating_battles' : (150, 475),
            'winrate' : (553, 475),
        }
        self.rating_league_label = _center_x, 470,
        self.rating_league_icon = _center_x - Leagues.empty.size[0]//2, 340,
        self.rating_stats = {
            'winrate' : (150, 390),
            'rating' : (_center_x, 395),
            'battles' : (553, 390),
        }
        self.rating_diff_stats = {
            'winrate' : (150, 425),
            'rating' : (_center_x, 425),
            'battles' : (553, 425),
        }
        self.tank_name = (_center_x, 570)
        self.tank_stats = {
            'winrate' : (150, 650),
            'avg_damage' : (_center_x, 650),
            'battles' : (553, 650)
        }
        self.tank_diff_stats = {
            'winrate' : (150, 690),
            'avg_damage' : (_center_x, 690),
            'battles' : (553, 690)
        }
        self.tank_labels = {
            'winrate' : (150, 730),
            'avg_damage' : (_center_x, 730),
            'battles' : (553, 730)
        }


class DiffValues():
    def __init__(self, diff_data: SesionDiffData) -> None:
        self.val_normalizer = ValueNormalizer()
        self.main = {
            'winrate' : self.value_colors(diff_data.main.winrate) + self.val_normalizer.winrate(diff_data.main.winrate),
            'avg_damage' : self.value_colors(diff_data.main.avg_damage) + self.val_normalizer.other(diff_data.main.avg_damage),
            'battles' : self.value_colors(diff_data.main.battles) + self.val_normalizer.other(diff_data.main.battles)
        }
        self.rating = {
            'winrate' : self.value_colors(diff_data.rating.winrate) + self.val_normalizer.winrate(diff_data.rating.winrate),
            'rating' : self.value_colors(diff_data.rating.rating) + self.val_normalizer.other(diff_data.rating.rating),
            'battles' : self.value_colors(diff_data.rating.battles) + self.val_normalizer.other(diff_data.rating.battles)
        }
        self.tank = {
            'winrate' : self.value_colors(diff_data.tank.winrate) + self.val_normalizer.winrate(diff_data.tank.winrate),
            'avg_damage' : self.value_colors(diff_data.tank.avg_damage) + self.val_normalizer.other(diff_data.tank.avg_damage),
            'battles' : self.value_colors(diff_data.tank.battles) + self.val_normalizer.other(diff_data.tank.battles)
        }

    def value_colors(self, value: int | float) -> str:
        if value > 0:
            return '+'
        else:
            return ''

class Values():
    def __init__(self, data: PlayerGlobalData, tank_index: int) -> None:
        self.val_normalizer = ValueNormalizer()
        stats_data = data.data.statistics
        tank_data = data.data.tank_stats
        self.main = {
            'winrate' : self.val_normalizer.winrate(stats_data.all.winrate),
            'avg_damage' : self.val_normalizer.other(stats_data.all.avg_damage),
            'battles' : self.val_normalizer.other(stats_data.all.battles)
        }
        self.rating = {
            'winrate' : self.val_normalizer.winrate(stats_data.rating.winrate),
            'rating' : self.val_normalizer.other(stats_data.rating.rating),
            'battles' : self.val_normalizer.other(stats_data.rating.battles)
        }
        self.tank = {
            'winrate' : self.val_normalizer.winrate(tank_data[tank_index].all.winarte),
            'avg_damage' : self.val_normalizer.other(tank_data[tank_index].all.avg_damage),
            'battles' : self.val_normalizer.other(tank_data[tank_index].all.battles)
        }

class ImageGen():
    cache = ImageCache()
    colors = Colors()
    fonts = Fonts()
    coord = None
    diff_values = None
    diff_data = None
    img_size = None
    leagues = None
    values = None
    image = None
    data = None
    text = None

    def generate(self, data: PlayerGlobalData, diff_data: SesionDiffData):
        self.diff_data = diff_data
        self.data = data
        self.diff_values = DiffValues(diff_data)
        self.values = Values(data, self.diff_data.tank_index)
        
        try:
            self.curr_tank_name = TanksDB().get_tank_by_id(str(self.diff_data.tank_id))['name']
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
            _log.debug('Image was sent in %s sec.', round(time() - strt_time, 4))
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

        self.draw_main_stats(img_draw)
        self.draw_main_diff_stats(img_draw)

        self.draw_tank_name(img_draw)
        self.draw_tank_stats(img_draw)
        self.draw_tank_diff_stats(img_draw)
        self.draw_tank_labels(img_draw)
        
        return_data = {'img': self.image, 'timestamp': datetime.now().timestamp(), 'id': str(data.id)}
        
        if need_caching:
            self.cache.add_item(return_data)
            _log.debug('Image added to cache')

        bin_image = BytesIO()
        self.image.save(bin_image, 'PNG')
        bin_image.seek(0)
        _log.debug('Image was sent in %s sec.', round(time() - strt_time, 4))

        return bin_image
    
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
            fill=self.colors.grey)
        
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
                fill=self.value_colors(getattr(self.diff_data.main, i))
            )

    def draw_tank_name(self, img: ImageDraw.ImageDraw):
        img.text(
            self.coord.tank_name,
            text=self.curr_tank_name,
            font=self.fonts.roboto_medium,
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
                fill=self.value_colors(getattr(self.diff_data.rating, i))
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
                fill=self.value_colors(getattr(self.diff_data.tank, i))
            )
    

    def draw_tank_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.tank_labels.keys():
            img.text(
                self.coord.tank_labels[i],
                text=getattr(self.text.data.for_image, i),
                font=self.fonts.roboto_small,
                anchor='ma',
                align='center',
                fill=self.colors.blue
            )


    def value_colors(self, value: int | float) -> tuple:
        if type(value) is str:
            return self.colors.grey
        if value > 0:
            return self.colors.green
        if value < 0:
            return self.colors.red
        if value == 0:
            return self.colors.grey

    def test(self, data: object, diff_data: object) -> None:
        return self.generate(data, diff_data)

if __name__ == '__main__':
    from lib.api import async_wotb_api
    from lib.data_parser import parse_data
    data = async_wotb_api.test('cnJIuHTeP_KPbIca', region='ru', save_to_database=False)
    diff_data = parse_data.get_session_stats(
        PlayerGlobalData(PlayersDB().get_member_last_stats(766019191836639273)), data)
    ImageGen().test(data, diff_data)
    input()
