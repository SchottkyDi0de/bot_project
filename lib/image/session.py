import base64
from enum import Enum
from io import BytesIO
from time import time
from typing import Dict

from discord.ext import commands
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageColor

from lib.data_classes.api.api_data import PlayerGlobalData
from lib.data_classes.db_player import (
    DBPlayer, ImageSettings, StatsViewSettings, WidgetSettings
)
from lib.data_classes.db_server import ServerSettings
from lib.data_classes.image import ImageGenExtraSettings
from lib.data_classes.locale_struct import Localization
from lib.data_classes.session import SessionDiffData, TankSessionData
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.image.common import ValueNormalizer
from lib.image.for_image.colors import Colors
from lib.image.for_image.flags import Flags
from lib.image.for_image.fonts import Fonts
from lib.image.for_image.icons import StatsIcons
from lib.image.for_image.stats_coloring import colorize
from lib.image.for_image.watermark import Watermark
from lib.locale.locale import Text
from lib.logger.logger import get_logger
from lib.utils.color_converter import get_tuple_from_color
from lib.settings.settings import Config
from lib.utils.singleton_factory import singleton
from lib.image.utils.resizer import center_crop

_log = get_logger(__file__, 'ImageSessionLogger', 'logs/image_session.log')
_config = Config().get()


class BlockTypes(Enum):
    main_stats = 0
    rating_stats = 1
    full_tank_stats = 2
    short_tank_stats = 3


class Leagues:
    """A class that holds different league images."""
    empty = Image.open('res/image/leagues/no-rating.png', formats=['png'])  # Empty league image
    gold = Image.open('res/image/leagues/gold.png', formats=['png'])  # Gold league image
    platinum = Image.open('res/image/leagues/platinum.png', formats=['png'])  # Platinum league image
    brilliant = Image.open('res/image/leagues/brilliant.png', formats=['png'])  # Brilliant league image
    calibration = Image.open('res/image/leagues/calibr.png', formats=['png'])  # Calibration league image


class BlocksStack():
    def __init__(self):
        self.small_blocks = 0
        self.blocks = 0
        
        self.max_blocks = 3
        self.max_small_blocks = 2
        
    def set_max_blocks(self, blocks: int, small_blocks: int):
        self.max_blocks = blocks
        self.max_small_blocks = small_blocks
        
    def add_blocks(self, val: int):
        for _ in range(val):
            if self.blocks < self.max_blocks:
                self.blocks += 1
            elif self.small_blocks < self.max_small_blocks:
                self.small_blocks += 1
            else:
                break
            
    def add_block(self):
        if self.blocks < self.max_blocks:
            self.blocks += 1
        elif self.small_blocks < self.max_small_blocks:
            self.small_blocks += 1
        else:
            pass
        
    def get_blocks(self) -> tuple[int, int]:
        return self.blocks, self.small_blocks
        
    def clear(self):
        self.blocks = 0
        self.small_blocks = 0


class Cache():
    cache_label = Image.open('res/image/other/cached_label.png', formats=['png'])


class RelativeCoordinates():
    def __init__(self, image_size, view_settings: StatsViewSettings):
        """
        Class to store coordinates for labels and stats in an image.

        Args:
        - img_size (tuple): Size of the image (width, height)
        """
        
        self.slots = len(view_settings.slots.keys())
        self.x_coords = []
        
        for index in range(self.slots + 1):
            if index == 0:
                continue
            
            self.x_coords.append(image_size[0]//(self.slots + 1) * index)
            
        self.center_x = image_size[0] // 2
        
    def blocks_labels(self, offset_y):
        return (self.center_x, offset_y + 15)

        # Main stats labels position in the stats block
    def main_stast_labels(self, offset_y) -> Dict[str, tuple]:
        coords = {}
        
        for index in range(self.slots):
            coords[f'slot_{index + 1}'] = (self.x_coords[index], offset_y + 196)
            
        return coords
        
    def main_stats_icons(self, offset_y, icons_size: tuple[int, int]):
        
        coords = {}
        
        for index in range(self.slots):
            coords[f'slot_{index + 1}'] = (self.x_coords[index] - icons_size[1] // 2, offset_y + 40)
            
        return coords
        
    def tank_stats_icons(self, offset_y, icons_size: tuple[int, int]):
        return self.main_stats_icons(offset_y, icons_size)
    
    def rating_stats_icons(self, offset_y, icons_size: tuple[int, int]):
        return {
            'winrate': (150 - icons_size[1] // 2, offset_y + 40),  # Winrate icon
            'battles': (553 - icons_size[1] // 2, offset_y + 40),  # Battles icon
        }

    # Main stats values position in the stats block
    def main_stats(self, offset_y):
        coords = {}
        
        for index in range(self.slots):
            coords[f'slot_{index + 1}'] = (self.x_coords[index], offset_y + 97)
            
        return coords

    # Main session stats position in the stats block
    def main_session_stats(self, offset_y):
        coords = {}
        
        for index in range(self.slots):
            coords[f'slot_{index + 1}'] = (self.x_coords[index], 140 + offset_y)
        
        return coords

    # Main difference stats position in the stats block
    def main_diff_stats(self, offset_y):
        coords = {}
        
        for index in range(self.slots):
            coords[f'slot_{index + 1}'] = (self.x_coords[index], 170 + offset_y)
            
        return coords

    # Rating labels
    def rating_labels(self, offset_y):
        return {
            'winrate': (150, 225 + offset_y),  # Winrate label
            'battles': (553, 225 + offset_y),  # Battles label
        }
        
    def rating_league_label(self, offset_y) -> tuple[int]:
        return (self.center_x, offset_y + 225)
    
    def rating_league_icon(self, offset_y) -> tuple[int]:
        icon_width = Leagues.empty.size[0]
        return (self.center_x - icon_width // 2, offset_y + 40)
        
    def rating_stats(self, offset_y):
        return {
            'winrate': (150, 102 + offset_y),  # Winrate stat
            'rating': (self.center_x, 102 + offset_y),  # Rating stat
            'battles': (553, 102 + offset_y),  # Battles stat
        }
    
    def rating_session_stats(self, offset_y):
        return {
            'winrate': (150, 152 + offset_y),  # Winrate session stats
            'rating': (self.center_x, 152 + offset_y),  # Rating session stats
            'battles': (553, 152 + offset_y),  # Battles session stats
        }
        
    def rating_diff_stats(self, offset_y):
        return {
            'winrate': (150, 190 + offset_y),  # Winrate difference stats
            'rating': (self.center_x, 190 + offset_y),  # Rating difference stats
            'battles': (553, 190 + offset_y),  # Battles difference stats
        }
        
    def tank_stats_labels(self, offset_y):
        coords = {}
        
        for index in range(self.slots):
            coords[f'slot_{index + 1}'] = (self.x_coords[index], 213 + offset_y)
            
        return coords
    
    def short_tank_stats_labels(self, offset_y):
        coords = {}
        
        for index in range(self.slots):
            coords[f'slot_{index + 1}'] = (self.x_coords[index], 150 + offset_y)
            
        return coords
        
    def short_tank_stats(self, offset_y: int):
        coords = {}
        
        for index in range(self.slots):
            coords[f'slot_{index + 1}'] = (self.x_coords[index], 90 + offset_y)
            
        return coords
        
    def tank_stats(self, offset_y: int):
        coords = {}
        
        for index in range(self.slots):
            coords[f'slot_{index + 1}'] = (self.x_coords[index], 105 + offset_y)
            
        return coords
        
    def tank_session_stats(self, offset_y: int):
        coords = {}
        
        for index in range(self.slots):
            coords[f'slot_{index + 1}'] = (self.x_coords[index], 150 + offset_y)
            
        return coords
        
    def tank_diff_stats(self, offset_y: int):
        coords = {}
        
        for index in range(self.slots):
            coords[f'slot_{index + 1}'] = (self.x_coords[index], 185 + offset_y)
            
        return coords

    def short_tank_session_stats(self, offset_y: int):
        coords = {}
        
        for i in range(self.slots):
            coords[f'slot_{i + 1}'] = (self.x_coords[i], 120 + offset_y)
            
        return coords


class DiffValues():
    def __init__(self, diff_data: SessionDiffData, stats_view: StatsViewSettings) -> None:
        """
        Initializes a DiffValues object with the given diff_data.

        Args:
            diff_data (SessionDiffData): The diff_data object containing the differences.

        Returns:
            None
        """
        self.val_normalizer = ValueNormalizer()
        self.diff_data = diff_data
        self.stats_view = stats_view
        self.main = {}
        
        for index, (_, value) in enumerate(stats_view.slots.items()):
            if value == 'empty':
                continue
            
            stats = getattr(diff_data.main_diff, value)
            
            if value == 'winrate' or value == 'accuracy':
                self.main.setdefault('slot_' + str(index + 1), (self.value_add_plus(stats) + self.val_normalizer.winrate(stats)))
                
            else:
                self.main.setdefault('slot_' + str(index + 1), (self.value_add_plus(stats) + self.val_normalizer.adaptive(stats)))

        self.rating = {
            'winrate': self.value_add_plus(diff_data.rating_diff.winrate) + self.val_normalizer.winrate(diff_data.rating_diff.winrate),
            'rating': self.value_add_plus(diff_data.rating_diff.rating) + self.val_normalizer.other(diff_data.rating_diff.rating),
            'battles': self.value_add_plus(diff_data.rating_diff.battles) + self.val_normalizer.other(diff_data.rating_diff.battles)
        }
        
    def tank_stats(self, tank_id: int | str):
        tank_id = str(tank_id)
        result = {}
        
        for slot, value in self.stats_view.slots.items():
            stats = getattr(self.diff_data.tank_stats[tank_id], 'd_' + value)
            
            if value == 'empty':
                continue
            
            if value == 'winrate' or value == 'accuracy':
                result[slot] = self.value_add_plus(stats) + self.val_normalizer.winrate(stats)
            
            else:
                result[slot] = self.value_add_plus(stats) + self.val_normalizer.adaptive(stats)
            
        return result

    def value_add_plus(self, value: int | float) -> str:
        """
        Determines if the given value is positive or negative and returns the corresponding symbol.

        Args:
            value (int | float): The value to be evaluated.

        Returns:
            str: The symbol '+' if the value is positive, otherwise an empty string.
        """
        if round(value, 2) > 0:
            return '+'
        else:
            return ''

class SessionValues():
    def __init__(self, session_data: SessionDiffData, stats_view: StatsViewSettings) -> None:
        self.val_normalizer = ValueNormalizer()
        self.session_data = session_data
        self.stats_view = stats_view
        self.main = {}
        
        for slot, value in self.stats_view.slots.items():
            if value in ['winrate', 'accuracy']:
                self.main[slot] = self.val_normalizer.winrate(getattr(session_data.main_session, value))
            else:
                self.main[slot] = self.val_normalizer.adaptive(getattr(session_data.main_session, value))

        self.rating = {
            'winrate': self.val_normalizer.winrate(session_data.rating_session.winrate, True),
            'rating': self.val_normalizer.other(session_data.rating_session.rating, True),
            'battles': self.val_normalizer.other(session_data.rating_session.battles, True)
        }

    def tank_stats(self, tank_id: int | str):
        tank_id = str(tank_id)
        tank_stats = {}
        
        for slot, value in self.stats_view.slots.items():
            if value in ['winrate', 'accuracy']:
                tank_stats[slot] = self.val_normalizer.winrate(getattr(self.session_data.tank_stats[tank_id], 's_' + value))
            else:
                tank_stats[slot] = self.val_normalizer.adaptive(getattr(self.session_data.tank_stats[tank_id], 's_' + value))
        
        return tank_stats


class Values():
    def __init__(self, data: PlayerGlobalData, session_diff: SessionDiffData, stats_view: StatsViewSettings) -> None:
        """
        Initializes a Values object.

        Args:
            data (PlayerGlobalData): The player's global data.
            tank_index (int): The index of the tank in the tankopedia_db list.
        """
        self.val_normalizer = ValueNormalizer()
        stats_data = data.data.statistics
        self.tank_data = data.data.tank_stats
        self.stats_view = stats_view
        self.session_diff = session_diff
        # Define the main statistics
        self.main = {}
        
        for slot, value in stats_view.slots.items():
            if value in ['winrate', 'accuracy']:
                self.main[slot] = self.val_normalizer.winrate(getattr(stats_data.all, value))
            else:
                self.main[slot] = self.val_normalizer.adaptive(getattr(stats_data.all, value))

        # Define the rating statistics
        rating = 0
        if stats_data.rating.calibration_battles_left == 0:
            rating = stats_data.rating.rating
        else:
            rating = f'{abs(stats_data.rating.calibration_battles_left - 10)} / 10'
            
        self.rating = {
            'winrate': self.val_normalizer.winrate(stats_data.rating.winrate),
            'rating': self.val_normalizer.other(rating, str_bypass=True),
            'battles': self.val_normalizer.other(stats_data.rating.battles)
        }

    def get_tank_stats(self, tank_id: int | str):
        tank_stats = {}
        
        for slot, value in self.stats_view.slots.items():
            if value in ['winrate', 'accuracy']:
                tank_stats[slot] = self.val_normalizer.winrate(getattr(self.tank_data[str(tank_id)].all, value))
            else:
                tank_stats[slot] = self.val_normalizer.adaptive(getattr(self.tank_data[str(tank_id)].all, value))
                
        return tank_stats

class StatsBlockSize:
    main_stats = 240
    rating_stats = 260
    full_tank_stats = 260
    short_tank_stats = 200


class BlockOffsets:
    first_indent = 80
    block_indent = 20
    horizontal_indent = 50


class ImageSize:
    max_height: int = 1350
    min_height: int = 380
    max_width: int = 800
    min_width: int = 525

class LayoutDefiner:
    def __init__(
            self, 
            data: SessionDiffData, 
            image_settings: ImageSettings, 
            extra: ImageGenExtraSettings,
            stats_view_settings: StatsViewSettings,
            widget_settings: WidgetSettings,
            widget_mode: bool
        ) -> None:
        self.stack = BlocksStack()
        self.widget_mode = widget_mode
        self.data = data
        self.image_height = ImageSize.min_height
        self.image_width = ImageSize.min_width
        self.blocks = 1
        self.small_blocks = 0
        self.max_fullstats_blocks = widget_settings.max_stats_blocks if widget_mode else 4
        self.max_short_stats_blocks = widget_settings.max_stats_small_blocks if widget_mode else 2
        self.image_settings = image_settings
        self.include_rating = False
        self.extra = extra
        self.widget_settings = widget_settings
        self.stats_view = stats_view_settings
        
    def _calculate_stats_blocks(self) -> None:
        self.stack.set_max_blocks(
            self.widget_settings.max_stats_blocks if self.widget_mode else 3,
            self.widget_settings.max_stats_small_blocks if self.widget_mode else 2
        )
        tanks_count = len(self.data.tank_stats)
        self.stack.add_blocks(tanks_count)
        
        if not self.image_settings.disable_rating_stats:
            include_rating = self.data.rating_session.battles > 0
        else:
            include_rating = False
            
        self.include_rating = include_rating
        
        if not (self.widget_mode and self.widget_settings.disable_main_stats_block):
            self.stack.add_block()

        if include_rating:
            self.stack.add_block()
        
        self.blocks, self.small_blocks = self.stack.get_blocks()
        _log.debug(f'Blocks: {self.blocks}, small blocks: {self.small_blocks}')
        
    def _calculate_image_size(self) -> None:
        if self.blocks == 3 and self.small_blocks == 2:
            self.image_height = ImageSize.max_height 
            self.image_width = ImageSize.max_width
            return
        
        self.image_height = BlockOffsets.first_indent
        
        self.image_height += (
            BlockOffsets.block_indent * (self.blocks + self.small_blocks) +
            StatsBlockSize.full_tank_stats * self.blocks +
            StatsBlockSize.short_tank_stats * self.small_blocks
        )
        
        if self.widget_settings.adaptive_width and self.widget_mode:
            self.image_width = (
                len(self.stats_view.slots.keys()) * (ImageSize.max_width // 4)
            )
            if self.image_width < ImageSize.min_width:
                self.image_width = ImageSize.min_width
        else:
            self.image_width = ImageSize.max_width
        
    def _prepare_background(self):
        self.layout_map = Image.new(
            'RGBA',
            (self.image_width, self.image_height),
            (0, 0, 0, 0)
        )
        
    def get_blocks_count(self) -> tuple[int, int]:
        return self.blocks, self.small_blocks

    def create_rectangle_map(self) -> Image.Image:
        self._calculate_stats_blocks()
        self._calculate_image_size()
        self._prepare_background()
        
        _log.debug(
            f'img size: {self.image_width}x{self.image_height} blocks: {self.blocks} small: {self.small_blocks}'
            )
        drawable_layout = ImageDraw.Draw(self.layout_map)
        current_offset = BlockOffsets.first_indent
        color = (
            *get_tuple_from_color(self.widget_settings.stats_block_color),
            int(self.widget_settings.stats_blocks_transparency * 255)
        )
        if not self.widget_mode:
            color = (255, 255, 255, 255)
        
        first_block = True

        for _ in range(self.blocks):
            if first_block and (self.widget_mode and self.widget_settings.disable_main_stats_block):
                first_block = False
            
            drawable_layout.rounded_rectangle(
                (
                    BlockOffsets.horizontal_indent, 
                    current_offset,
                    self.image_width - BlockOffsets.horizontal_indent,
                    (StatsBlockSize.main_stats if first_block else StatsBlockSize.full_tank_stats) + current_offset
                ),
                fill=color,
                radius=25
            )
            if first_block:
                current_offset += StatsBlockSize.main_stats
            else:
                current_offset += StatsBlockSize.full_tank_stats
                
            current_offset += BlockOffsets.block_indent
            first_block = False
         
        if self.small_blocks > 0:
            for _ in range(self.small_blocks):
                drawable_layout.rounded_rectangle(
                    (
                        BlockOffsets.horizontal_indent, 
                        current_offset, 
                        self.image_width - BlockOffsets.horizontal_indent,
                        current_offset + StatsBlockSize.short_tank_stats
                    ),
                    fill=color,
                    radius=25
                )
                current_offset += StatsBlockSize.short_tank_stats + BlockOffsets.block_indent
        
        return self.layout_map
    
    
class ImageOutputType(Enum):
    bytes_io = 0
    pil_image = 1


@singleton
class ImageGen():
    leagues = Leagues()
    colors = Colors()
    pdb = PlayersDB()
    sdb = ServersDB()
    flags = Flags()
    fonts = Fonts()
    stats_view: StatsViewSettings = None
    session_values: SessionValues = None
    diff_data: SessionDiffData = None
    diff_values: DiffValues = None
    image: Image.Image = None
    text: Localization = None
    img_size: tuple = None
    values: Values = None
    coord = None
    data = None
    
    
    def load_image(self, bytes_ot_path: str | BytesIO, return_img: bool = False) -> None:
        image = Image.open(bytes_ot_path)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        if return_img:
            return image
        
        self.image = image

    def generate(
            self, 
            data: PlayerGlobalData,
            diff_data: SessionDiffData,
            ctx: commands.Context | None,
            player: DBPlayer,
            server_settings: ServerSettings | None,
            test = False,
            debug_label = False,
            extra: ImageGenExtraSettings = ImageGenExtraSettings(),
            output_type: ImageOutputType = ImageOutputType.bytes_io,
            widget_mode: bool = False
            ) -> BytesIO | Image.Image:
        """
        Generate the image for the given player's session stats.

        Args:
            data (PlayerGlobalData): The global data of the player.
            diff_data (SessionDiffData): The diff data of the session.
            test (bool): If True, the image will be displayed for testing purposes. 

        Returns:
            BytesIO: The image generated for the session stats.
        """
        # widget_mode = True
        # player.widget_settings.adaptive_width = True
        # player.widget_settings.disable_bg = True
        # player.widget_settings.use_bg_for_stats_blocks = True
        
        self.player = player
        self.image_settings = player.image_settings
        self.layout_definer = LayoutDefiner(
            data=diff_data,
            image_settings=player.image_settings,
            extra=extra,
            stats_view_settings=player.session_settings.stats_view,
            widget_settings=player.widget_settings,
            widget_mode=widget_mode
            )
        self.layout_map = self.layout_definer.create_rectangle_map()
        self.blocks, self.small_blocks = self.layout_definer.get_blocks_count()
        self.include_rating = self.layout_definer.include_rating if not widget_mode else False
        self.diff_data = diff_data
        self.data = data
        self.diff_values = DiffValues(diff_data, player.session_settings.stats_view)
        self.session_values = SessionValues(diff_data, player.session_settings.stats_view)
        self.values = Values(data, diff_data, player.session_settings.stats_view)
        self.current_offset = 0
        self.tank_iterator = iter(diff_data.tank_stats)
        self.stats_view = player.session_settings.stats_view

        if ctx is not None:
            user_bg = self.pdb.get_member_image(ctx.author.id) is not None
            server_bg = self.sdb.get_server_image(ctx.guild.id) is not None
        else:
            user_bg = self.pdb.get_member_image(player.id) is not None

            server_bg = False
        
        if server_settings is not None:
            allow_custom_background = server_settings.allow_custom_backgrounds
        else:
            allow_custom_background = False

        if player.image_settings.use_custom_bg or server_bg:
            if user_bg and allow_custom_background:
                image_bytes = base64.b64decode(self.pdb.get_member_image(ctx.author.id))
                if image_bytes != None:
                    image_buffer = BytesIO(image_bytes)
                    self.image = Image.open(image_buffer)
                    self.load_image(image_buffer)
            
            elif server_bg:
                image_bytes = base64.b64decode(self.sdb.get_server_image(ctx.guild.id))
                if image_bytes != None:   
                    image_buffer = BytesIO(image_bytes)
                    self.load_image(image_buffer)
            else:
                self.image = Image.open('res/image/default_image/default_bg.png', formats=['png'])

                if self.image.mode != 'RGBA':
                    self.image.convert('RGBA').save('res/image/default_image/default_bg.png')
                    self.load_image(_config.image.default_bg_path)
        else:
            self.load_image(_config.image.default_bg_path)

            if self.image.mode != 'RGBA':
                self.image.convert('RGBA').save(_config.image.default_bg_path)
                self.load_image()

        self.image = center_crop(self.image, self.layout_map.size)

        start_time = time()
        self.img_size = self.image.size
        
        self.draw_background(
            self.layout_map, 
            extra=extra, 
            widget_mode=widget_mode, 
            widget_settings=player.widget_settings   
        )
        img_draw = ImageDraw.Draw(self.image)

        self.text = Text().get()
        self.coord = RelativeCoordinates(self.img_size, player.session_settings.stats_view)
        self.current_offset = BlockOffsets.first_indent

        if not (widget_mode and player.widget_settings.disable_nickname):
            self.draw_nickname(img_draw)
            if not self.image_settings.disable_flag:
                self.draw_flag()
        
        if not (widget_mode and player.widget_settings.disable_main_stats_block):
            self.draw_main_stats_block(img_draw)
            self.blocks -= 1
            self.current_offset += StatsBlockSize.main_stats + BlockOffsets.block_indent

        if self.include_rating:
            self.draw_rating_stats_block(img_draw)
            self.blocks -= 1
            self.current_offset += StatsBlockSize.rating_stats + BlockOffsets.block_indent

        for _ in range(self.blocks):
            try:
                curr_tank = self.diff_data.tank_stats[next(self.tank_iterator)]
            except StopIteration:
                break
            self.draw_tank_stats_block(img_draw, curr_tank)
            self.current_offset += StatsBlockSize.full_tank_stats + BlockOffsets.block_indent
            self.blocks -= 1
        
        for _ in range(self.small_blocks):
            try:
                curr_tank = self.diff_data.tank_stats[next(self.tank_iterator)]
            except StopIteration:
                break
            self.draw_short_tank_stats_block(img_draw, curr_tank)
            self.small_blocks -= 1
            self.current_offset += StatsBlockSize.short_tank_stats + BlockOffsets.block_indent
            
        self.draw_watermark()
            
        if debug_label:
            self.draw_debug_label(img_draw)

        if test:
            self.image.show()
            return
        
        if output_type == ImageOutputType.bytes_io:
            bin_image = BytesIO()
            self.image.save(bin_image, 'PNG')
            bin_image.seek(0)
            _log.debug('Image was sent in %s sec.', round(time() - start_time, 4))
            return bin_image
        
        if output_type == ImageOutputType.pil_image:
            return self.image
    
    def draw_main_stats_block(self, image_draw: ImageDraw.ImageDraw) -> None:
        self.draw_block_label(image_draw, self.text.for_image.main)
        self.draw_main_stats_icons()
        self.draw_main_labels(image_draw)
        self.draw_main_stats(image_draw)
        self.draw_main_session_stats(image_draw)
        self.draw_main_diff_stats(image_draw)
        
    def draw_rating_stats_block(self, image_draw: ImageDraw.ImageDraw) -> None:
        self.draw_block_label(image_draw, self.text.for_image.rating)
        self.draw_rating_icons()
        self.draw_rating_league()
        self.draw_rating_labels(image_draw)
        self.draw_rating_stats(image_draw)
        self.draw_rating_session_stats(image_draw)
        self.draw_rating_diff_stats(image_draw)
        
    def draw_tank_stats_block(self, image_draw: ImageDraw.ImageDraw, curr_tank: TankSessionData) -> None:
        self.draw_tank_block_label(image_draw, curr_tank)
        self.draw_tank_stats_icons()
        self.draw_tank_labels(image_draw)
        self.draw_tank_stats(image_draw, curr_tank)
        self.draw_tank_session_stats(image_draw, curr_tank)
        self.draw_tank_diff_stats(image_draw, curr_tank)
        
    def draw_short_tank_stats_block(self, image_draw: ImageDraw.ImageDraw, curr_tank: TankSessionData) -> None:
        self.draw_tank_block_label(image_draw, curr_tank)
        self.draw_tank_stats_icons()
        self.draw_short_tank_labels(image_draw)
        self.draw_short_tank_stats(image_draw, curr_tank)
        self.draw_short_tank_session_stats(image_draw, curr_tank)

    def draw_main_stats_icons(self) -> None:
        for slot, value in self.stats_view.slots.items():
            icon: Image.Image = getattr(StatsIcons, value)
            self.image.paste(
                icon,
                self.coord.main_stats_icons(self.current_offset, icon.size)[slot],
                icon
            )
        
    def draw_rating_icons(self) -> None:
        for i in self.coord.rating_stats_icons(self.current_offset, (0, 0)).keys():
            icon: Image.Image = getattr(StatsIcons, i)
            self.image.paste(
                icon,
                self.coord.rating_stats_icons(self.current_offset, icon.size)[i],
                icon
            )
        
    def draw_tank_stats_icons(self) -> None:
        for slot, value in self.stats_view.slots.items():
            icon: Image.Image = getattr(StatsIcons, value)
            self.image.paste(
                icon,
                self.coord.tank_stats_icons(self.current_offset, icon.size)[slot],
                icon
        )
        
    def draw_block_label(self, img_draw: ImageDraw.ImageDraw, text: str) -> None:
        img_draw.text(
            self.coord.blocks_labels(self.current_offset),
            text,
            font=self.fonts.roboto_small,
            anchor='mm',
            fill=self.image_settings.main_text_color
        )
        
    def draw_tank_block_label(self, img_draw: ImageDraw.ImageDraw, curr_tank: TankSessionData) -> None:
        img_draw.text(
            self.coord.blocks_labels(self.current_offset),
            f'{self.tank_type_handler(curr_tank.tank_type)} {curr_tank.tank_name} {self.tank_tier_handler(curr_tank.tank_tier)}',
            font=self.fonts.roboto_icons,
            anchor='mm',
            fill=self.image_settings.main_text_color
        )
    
    def draw_background(
            self, 
            rectangle_map: Image.Image, 
            extra: ImageGenExtraSettings,
            widget_mode: bool,
            widget_settings: WidgetSettings
        ) -> None:
        
        if self.image_settings.disable_stats_blocks:
            return
        
        if widget_mode:
            image = Image.new('RGBA', rectangle_map.size, (0, 0, 0, 0))
            if widget_settings.disable_bg:
                self.image = image
                self.image.paste(rectangle_map, (0, 0), rectangle_map)
                
            elif widget_settings.use_bg_for_stats_blocks:
                bg = self.image.copy()
                _log.debug(f'BG size: {bg.size}')
                _log.debug(f'Rectangle map size: {rectangle_map.size}')
                self.image = image
                if bg.size != rectangle_map.size:
                    bg = bg.resize(rectangle_map.size)
                
                self.image.paste(bg, (0, 0), rectangle_map)
        
        else:
            bg = self.image.copy()
            
            gaussian_filter = ImageFilter.GaussianBlur(radius=self.image_settings.glass_effect)

            if self.image_settings.glass_effect > 0:
                bg = bg.filter(gaussian_filter)
            if self.image_settings.blocks_bg_opacity > 0:
                bg = ImageEnhance.Brightness(bg).enhance(self.image_settings.blocks_bg_opacity)
                bg.filter(gaussian_filter)

            self.image.paste(bg, (0, 0), rectangle_map)

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
        
    def draw_watermark(self):
        self.image.paste(Watermark.v1, (
            self.img_size[0] - 40, 
            self.img_size[1] // 2 - Watermark.v1.size[1] // 2
            ), 
        Watermark.v1)
        
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
                _log.warning(f'Ignoring Exception: Invalid tank type: {tank_type}')
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
                _log.warning(f'Ignoring Exception: Invalid tank tier: {tier}')
                return ' • ?'

    def draw_nickname(self, img: ImageDraw.ImageDraw):
        if self.image_settings.hide_nickname:
            self.data.nickname = '~nickname hidden~'
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
            
        if not self.image_settings.hide_nickname:
            img.text(
                (self.img_size[0]//2, 55),
                text=f'ID: {str(self.data.id)}',
                font=self.fonts.roboto_small2,
                anchor='ma',
                fill=Colors.l_grey)

    def draw_main_labels(self, img: ImageDraw.ImageDraw):
        coords = self.coord.main_stast_labels(self.current_offset)
        for slot, value in self.stats_view.slots.items():
            img.text(
                coords[slot],
                text=getattr(self.text.for_image, value),
                font=self.fonts.roboto_small,
                anchor='ma',
                align='center',
                fill=self.image_settings.stats_text_color
            )

    def draw_main_stats(self, img: ImageDraw.ImageDraw):
        coords = self.coord.main_stats(self.current_offset)
        for slot, value in self.stats_view.slots.items():
            img.text(
                coords[slot],
                text=self.values.main[slot],
                font=self.fonts.roboto,
                anchor='ma',
                align='center',
                fill=colorize(
                    value,
                    self.values.main[slot],
                    self.image_settings.stats_color
                    )
                )

    def draw_main_diff_stats(self, img: ImageDraw.ImageDraw):
        coords = self.coord.main_diff_stats(self.current_offset)
        for slot, value in self.stats_view.slots.items():
            img.text(
                coords[slot],
                text=self.diff_values.main[slot],
                font=self.fonts.roboto_medium,
                anchor='ma',
                align='center',
                fill=self.value_colors(getattr(self.diff_data.main_diff, value))
            )
    
    def draw_main_session_stats(self, img: ImageDraw.ImageDraw):
        coords = self.coord.main_session_stats(self.current_offset)
        for slot, value in self.stats_view.slots.items():
            img.text(
                coords[slot],
                text=self.session_values.main[slot],
                font=self.fonts.roboto_25,
                anchor='ma',
                align='center',
                fill=colorize(
                    value,
                    self.session_values.main[slot],
                    Colors.l_grey
                )
            )

    def draw_rating_labels(self, img: ImageDraw.ImageDraw):
        coords = self.coord.rating_labels(self.current_offset)
        for i in coords.keys():
            img.text(
                coords[i],
                text=getattr(self.text.for_image, i),
                font=self.fonts.roboto_small,
                anchor='ma',
                align='center',
                fill=self.image_settings.stats_text_color
            )
        self._rating_label_handler(img)

    def draw_rating_stats(self, img: ImageDraw.ImageDraw):
        coords = self.coord.rating_stats(self.current_offset)
        for i in coords.keys():
            img.text(
                coords[i],
                text=self.values.rating[i],
                font=self.fonts.roboto,
                anchor='ma',
                align='center',
                fill=colorize(
                    i,
                    self.values.rating[i],
                    self.image_settings.stats_color,
                    rating=True
                    )
                )
            
    def draw_rating_session_stats(self, img: ImageDraw.ImageDraw):
        coords = self.coord.rating_session_stats(self.current_offset)
        for i in coords.keys():
            img.text(
                coords[i],
                text=self.session_values.rating[i],
                font=self.fonts.roboto_25,
                anchor='ma',
                align='center',
                fill=colorize(
                    i,
                    self.session_values.rating[i],
                    Colors.l_grey,
                    rating=True
                )
            )

    def draw_rating_league(self) -> None:
        coords = self.coord.rating_league_icon(self.current_offset)
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

        self.image.paste(rt_img, coords, rt_img)

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
            self.coord.rating_league_label(self.current_offset),
            text=text,
            font=self.fonts.roboto_small,
            anchor='ma',
            align='center',
            fill=Colors.blue
        )

    def draw_rating_diff_stats(self, img: ImageDraw.ImageDraw):
        coords = self.coord.rating_diff_stats(self.current_offset)
        for i in coords.keys():
            img.text(
                coords[i],
                text=self.diff_values.rating[i],
                font=self.fonts.roboto_medium,
                anchor='ma',
                align='center',
                fill=self.value_colors(getattr(self.diff_data.rating_diff, i))
            )
        self._rating_label_handler(img)

    def draw_tank_stats(self, img: ImageDraw.ImageDraw, curr_tank: TankSessionData):
        coords = self.coord.tank_stats(self.current_offset)
        tank_stats = self.values.get_tank_stats(curr_tank.tank_id)
        for slot, value in self.stats_view.slots.items():
            img.text(
                coords[slot],
                text=tank_stats[slot],
                font=self.fonts.roboto,
                anchor='ma',
                align='center',
                fill=colorize(
                    value,
                    tank_stats[slot],
                    self.image_settings.stats_color
                )
            )
    
    def draw_short_tank_stats(self, img: ImageDraw.ImageDraw, curr_tank: TankSessionData):
        coords = self.coord.short_tank_stats(self.current_offset)
        tank_stats = self.values.get_tank_stats(curr_tank.tank_id)
        for slot, value in self.stats_view.slots.items():
            img.text(
                coords[slot],
                text=tank_stats[slot],
                font=self.fonts.roboto,
                anchor='ma',
                align='center',
                fill=colorize(
                    value,
                    tank_stats[slot],
                    self.image_settings.stats_color
                    )
            )

    def draw_short_tank_session_stats(self, img: ImageDraw.ImageDraw, curr_tank: TankSessionData):
        coords = self.coord.short_tank_session_stats(self.current_offset)
        for slot, value in self.stats_view.slots.items():
            img.text(
                coords[slot],
                text=self.session_values.tank_stats(curr_tank.tank_id)[slot],
                font=self.fonts.roboto_25,
                anchor='ma',
                align='center',
                fill=self.value_colors(getattr(curr_tank, f'd_{value}'))
            )
                
    def draw_tank_diff_stats(self, img: ImageDraw.ImageDraw, curr_tank: TankSessionData):
        coords = self.coord.tank_diff_stats(self.current_offset)
        tank_stats = self.diff_values.tank_stats(curr_tank.tank_id)
        for slot, value in self.stats_view.slots.items():
            img.text(
                coords[slot],
                text=tank_stats[slot],
                font=self.fonts.roboto_medium,
                anchor='ma',
                align='center',
                fill=self.value_colors(getattr(curr_tank, f'd_{value}'))
            )

    def draw_tank_session_stats(self, img: ImageDraw.ImageDraw, curr_tank: TankSessionData):
        coords = self.coord.tank_session_stats(self.current_offset)
        tank_stats = self.session_values.tank_stats(curr_tank.tank_id)
        for slot, value in self.stats_view.slots.items():
            img.text(
                coords[slot],
                text=tank_stats[slot],
                font=self.fonts.roboto_25,
                anchor='ma',
                align='center',
                fill=colorize(
                    value,
                    tank_stats[slot],
                    Colors.l_grey
                )
            )

    def draw_tank_labels(self, img: ImageDraw.ImageDraw):
        coords = self.coord.tank_stats_labels(self.current_offset)
        for slot, value in self.stats_view.slots.items():
            img.text(
                coords[slot],
                text=getattr(self.text.for_image, value),
                font=self.fonts.roboto_small,
                anchor='ma',
                align='center',
                fill=self.image_settings.stats_text_color
            )
            
    def draw_short_tank_labels(self, img: ImageDraw.ImageDraw):
        coords = self.coord.short_tank_stats_labels(self.current_offset)
        for slot, value in self.stats_view.slots.items():
            img.text(
                coords[slot],
                text=getattr(self.text.for_image, value),
                font=self.fonts.roboto_small,
                anchor='ma',
                align='center',
                fill=self.image_settings.stats_text_color
            )
    
    def draw_flag(self) -> None:
        match self.data.region:
            case 'ru':
                self.image.paste(self.flags.ru, (10, 10), self.flags.ru)
            case 'eu':
                self.image.paste(self.flags.eu, (10, 10), self.flags.eu)
            case 'com':
                self.image.paste(self.flags.usa, (10, 10), self.flags.usa)
            case 'asia':
                self.image.paste(self.flags.china, (10, 10), self.flags.china)

    def value_colors(self, value: int | float) -> tuple:
        if type(value) is str:
            return Colors.grey
        value = round(value, 2)
        if value > 0:
            return self.image_settings.positive_stats_color
        if value < 0:
            return self.image_settings.negative_stats_color
        if value == 0:
            return Colors.grey
