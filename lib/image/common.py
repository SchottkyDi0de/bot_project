'''
Модуль для генерирования изображения
со статистикой
'''
from io import BytesIO
from enum import Enum
from time import time
from copy import deepcopy
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from lib.data_classes.api.api_data import PlayerGlobalData
from lib.image.for_image.colors import Colors
from lib.image.for_image.fonts import Fonts
from lib.image.for_image.icons import StatsIcons
from lib.image.for_image.medals import Medals
from lib.image.utils.b64_img_handler import img_to_base64, base64_to_img, img_to_readable_buffer
from lib.image.for_image.watermark import Watermark
from lib.image.utils.resizer import center_crop
from lib.logger.logger import get_logger
from lib.settings.settings import Config
from lib.utils.singleton_factory import singleton
from lib.image.for_image.stats_coloring import colorize
from lib.image.for_image.icons import LeaguesIcons
from lib.image.utils.val_normalizer import ValueNormalizer

from lib.data_classes.db_player import ImageSettings
from lib.locale.locale import Text

if TYPE_CHECKING:
    from lib.data_classes.image import CommonImageGenExtraSettings  
    from lib.data_classes.db_player import AccountSlotsEnum, DBPlayer, GameAccount

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
    

class ImageGenReturnTypes(Enum):
    PIL_IMAGE = 1
    BYTES_IO = 2
    BASE64 = 3


@singleton
class ImageGenCommon():
    image_settings = ImageSettings()
    text = None
    fonts = Fonts()
    leagues = LeaguesIcons()
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
    
    def _load_image(self, bytes_ot_path: str | bytes | None) -> None:
        if bytes_ot_path is not None:
            image = Image.open(_config.image.default_bg_path, formats=['png'])
        else:
            image = Image.open(bytes_ot_path, formats=['png'])
            
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        self.image = center_crop(image, (ImageSize.max_width, ImageSize.max_height))

    def _load_image_by_rules(self, member: 'DBPlayer | None' = None) -> None:
        if member is not None:
            if (member.image is not None) and member.use_custom_image:
                self.image = base64_to_img(member.image)
                return
                
        self._load_image(_config.image.default_bg_path)


    def generate(
            self,
            data: PlayerGlobalData,
            member: 'DBPlayer | None' = None,
            slot: 'AccountSlotsEnum | None' = None,
            force_image_settings: ImageSettings = None,
            force_image: BytesIO | None = None,
            extra: 'CommonImageGenExtraSettings | None' = None,
            debug_label: bool = False,
            return_image: ImageGenReturnTypes = ImageGenReturnTypes.BYTES_IO
        ) -> BytesIO | str | Image.Image:

        self.text = Text().get()
        start_time = time()
        
        if member is not None and slot is not None:
            game_account: 'GameAccount' = getattr(member.game_accounts, slot.name)
            image_settings = game_account.image_settings
        else:
            image_settings = ImageSettings()

        temp_im = force_image_settings if force_image_settings is not None else image_settings
        if extra:
            temp_im = deepcopy(temp_im)
            for name in extra.model_fields:
                setattr(temp_im, name, getattr(extra, name))
        
        self.image_settings = temp_im
        self.data = data
        self.values = Values(data)
        self.stat_all = data.data.statistics.all
        self.stat_rating = data.data.statistics.rating
        self.achievements = data.data.achievements
        
        if not force_image:
            self._load_image_by_rules(member=member)
        else:
            self._load_image(force_image.getvalue())
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

        _log.debug(f'Generate common image time: {round(time() - start_time, 4)} sec.')
        if return_image == ImageGenReturnTypes.PIL_IMAGE:
            return self.image
        elif return_image == ImageGenReturnTypes.BASE64:
            return img_to_base64(self.image)
        elif return_image == ImageGenReturnTypes.BYTES_IO:
            return img_to_readable_buffer(self.image)
        else:
            raise TypeError(f'return_image must be an instance of ImageGenReturnTypes enum, not {return_image.__class__.__name__}')

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
            font=self.fonts.roboto_25,
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
        if not self.image_settings.stats_blocks_transparency == 100:
            bg = ImageEnhance.Brightness(bg).enhance(self.image_settings.stats_blocks_transparency)

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
                'font':     self.fonts.roboto_30,
            }
            nickname = {
                'text':     self.data.nickname,
                'font':     self.fonts.roboto_30,
            }

            tag_length = img.textlength(**tag) + 10
            nick_length = img.textlength(**nickname)
            full_length = tag_length + nick_length

            img.text(
                xy=(self.img_size[0]//2 - tag_length//2, 20),
                text=self.data.nickname,
                font=self.fonts.roboto_30,
                anchor='ma',
                fill=self.image_settings.nickname_color)

            img.text(
                xy=(self.img_size[0]//2 + full_length//2 - tag_length//2, 20),
                text=tag['text'],
                font=self.fonts.roboto_30,
                anchor='ma',
                fill=self.image_settings.clan_tag_color)
        else:
            img.text(
                (self.img_size[0]//2, 20),
                text=self.data.nickname,
                font=self.fonts.roboto_30,
                anchor='ma',
                fill=self.image_settings.nickname_color
            )

        img.text(
            (self.img_size[0]//2, 55),
            text=f'ID: {str(self.data.id)}',
            font=self.fonts.roboto_17,
            anchor='ma',
            fill=Colors.l_grey)

    def draw_nickname_box(self, img: ImageDraw.ImageDraw):
        pass

    def draw_category_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.category_labels.keys():
            img.text(
                self.coord.category_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_20,
                anchor='mm',
                fill=self.image_settings.main_text_color
            )

    def draw_medals_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.medals_labels.keys():
            img.text(
                self.coord.medals_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_17,
                anchor='ma',
                align='center',
                fill=self.image_settings.stats_text_color
            )

    def draw_common_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.common_stats_labels.keys():
            img.text(
                self.coord.common_stats_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_17,
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
                font=self.fonts.roboto_17,
                anchor='ma',
                align='center',
                fill=self.image_settings.stats_text_color
            )

    def draw_rating_labels(self, img: ImageDraw.ImageDraw):
        for i in self.coord.rating_labels.keys():
            img.text(
                self.coord.rating_labels[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_17,
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
            font=self.fonts.roboto_17,
            anchor='ma',
            # align='center',
            fill=self.image_settings.stats_text_color
        )

    def draw_main_stats(self, img: Image.Image):
        for i in self.coord.main_stats.keys():
            img.text(
                self.coord.main_stats[i],
                text=self.values.main[i],
                font=self.fonts.roboto_30,
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
                font=self.fonts.roboto_30,
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
                font=self.fonts.roboto_30,
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
                font=self.fonts.roboto_17,
                anchor='ma',
                fill=self.image_settings.stats_color
            )

    def draw_main_points(self, img: Image.Image):
        for i in self.coord.main_stats_points.keys():
            img.text(
                self.coord.main_stats_points[i],
                text='.',
                font=self.fonts.roboto_100,
                anchor='mm',
                fill=self.point_coloring(i, getattr(self.data.data.statistics.all, i))
            )

    def draw_rating_points(self, img: Image.Image):
        for i in self.coord.main_stats_points.keys():
            img.text(
                self.coord.main_stats_points[i],
                text='.',
                font=self.fonts.roboto_100,
                anchor='mm',
                fill=self.point_coloring(i, getattr(self.data.data.statistics.all, i))
            )

    def draw_common_points(self, img: Image.Image):
        for i in self.coord.common_stats_point.keys():
            img.text(
                self.coord.common_stats_point[i],
                text='.',
                font=self.fonts.roboto_100,
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