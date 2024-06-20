from datetime import datetime, timedelta
from pprint import pprint
from time import time

import numpy
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from discord import ApplicationContext
import pytz

from lib.data_classes.db_player import DBPlayer
from lib.data_classes.locale_struct import Localization
from lib.image.utils.b64_img_handler import img_to_base64
from lib.utils.calculate_exp import get_level
from lib.utils.singleton_factory import singleton
from lib.locale.locale import Text
from lib.image.for_image.fonts import Fonts
from lib.image.for_image.colors import Colors


class ProfileImage:
    width = 840
    height = 520
    center_x = width // 2
    center_y = height // 2


class ProgressBar:
    width = int(ProfileImage.width - (ProfileImage.width * 0.1))
    height = 25
    h_offset = 25
    v_offset = int(ProfileImage.height * 0.9)
    color = Colors.orange
    
    layout_box_padding_x = 15
    layout_box_padding_y = 8
    layout_box_width = int(width + layout_box_padding_x)
    layout_box_height = int(height + layout_box_padding_y)
    text_offset = 30
    text_padding = 5
    
    
class Coords:
    nickname_block_indent_x = 140
    text_padding = 5
    blocks_indent_y = 10
    pb_x_offset = 35
    nickname_block = (
        nickname_block_indent_x, 
        8, 
        ProfileImage.width - nickname_block_indent_x, 
        35
    ) # (x0, y0, x1, y1)
    nickname_text = (ProfileImage.width // 2, 7) # (x, y)
    badges_box = (
        nickname_block_indent_x, 
        40,
        ProfileImage.width - nickname_block_indent_x, 
        105
    ) # (x0, y0, x1, y1)
    badges_text = (ProfileImage.width // 2, badges_box[1] + 5) # (x, y)
    progressbar = (ProgressBar.width - ProfileImage.width) // 2, ProfileImage.height - 10
    progressbar_box = (
        pb_x_offset,
        ProgressBar.v_offset - ProgressBar.layout_box_padding_y - ProgressBar.text_offset,
        ProfileImage.width - pb_x_offset,
        ProgressBar.v_offset + ProgressBar.layout_box_height
    ) # (x0, y0, x1, y1)
    progressbar_text_exp_rem = (
        progressbar_box[0] + ProgressBar.text_padding, 
        progressbar_box[1] + ProgressBar.text_padding,
    ) # (x, y)
    progressbar_text_exp_next = (
        progressbar_box[2] - ProgressBar.text_padding, 
        progressbar_box[3] - ProgressBar.layout_box_height - ProgressBar.text_offset,
    ) # (x, y)
    command_stats_box = (
        progressbar_box[0], badges_box[3] + blocks_indent_y,
        ProfileImage.center_x - blocks_indent_y, progressbar_box[1] - blocks_indent_y
    ) # (x0, y0, x1, y1)
    commands_stats_line = (
        command_stats_box[0] + text_padding,
        command_stats_box[1] + pb_x_offset + text_padding,
        command_stats_box[2] - text_padding,
        command_stats_box[1] + pb_x_offset + text_padding
    )    
    
    command_stats_main_text = (
        command_stats_box[3] // 2,
        command_stats_box[1] + text_padding
    )
    
    command_stats_sub_text_num = (
        command_stats_box[0] + text_padding,
        commands_stats_line[1] - 2
    )
    command_stats_sub_text_name = (
        command_stats_box[3] // 2,
        commands_stats_line[1] - 2
    )
    command_stats_sub_text_time = (
        command_stats_box[3] - text_padding * 3,
        commands_stats_line[1] - 2
    )
    
    commands_list_nums = (
        command_stats_box[0] + text_padding,
        command_stats_main_text[1] + pb_x_offset
    )
    commands_list_commands = (
        command_stats_main_text[0],
        command_stats_main_text[1] + pb_x_offset
    )
    commands_list_times = (
        command_stats_box[3] - text_padding * 2,
        command_stats_main_text[1] + pb_x_offset,
        
    )


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
    

class Badges:
    active_user = Image.open('res/image/profile/badges/active_user.png', formats=['png'])
    tester = Image.open('res/image/profile/badges/tester.png', formats=['png'])
    beta_tester = Image.open('res/image/profile/badges/beta_tester.png', formats=['png'])
    streamer = Image.open('res/image/profile/badges/streamer.png', formats=['png'])
    administrator = Image.open('res/image/profile/badges/administrator.png', formats=['png'])
    docs_contributor = Image.open('res/image/profile/badges/docs_contributor.png', formats=['png'])
    translator = Image.open('res/image/profile/badges/translator_v2.png', formats=['png'])
    theme_creator = Image.open('res/image/profile/badges/theme_creator.png', formats=['png'])
    dev = Image.open('res/image/profile/badges/dev.png', formats=['png'])
    premium = Image.open('res/image/profile/badges/premium_v2.png', formats=['png'])
    verified = Image.open('res/image/profile/badges/verified.png', formats=['png'])
    
    badge_size = (32, 32)
    badge_indent = 5
    
    active_user.thumbnail(badge_size)
    tester.thumbnail(badge_size)
    beta_tester.thumbnail(badge_size)
    streamer.thumbnail(badge_size)
    administrator.thumbnail(badge_size)
    docs_contributor.thumbnail(badge_size)
    translator.thumbnail(badge_size)
    theme_creator.thumbnail(badge_size)
    dev.thumbnail(badge_size)
    premium.thumbnail(badge_size)
    verified.thumbnail(badge_size)


class Fades:
    poly_grey = Image.open('res/image/profile/textures/poly_fade.png', formats=['png'])


@singleton
class ProfileImageGen:
    def __init__(self) -> None:
        self.img_avg_color: tuple[int, int, int] = None
        self.img_opposite_color: tuple[int, int, int] = None
        self.text: Localization = None
        self.img: Image.Image = None
        self.img_draw: ImageDraw.ImageDraw = None
        self.member: DBPlayer = None
        self.ctx: ApplicationContext = None
        self.opposite_bg_brightness = 0.5
        
    def generate(self, member: DBPlayer, ctx: ApplicationContext) -> str:
        s_time = time()
        self.member = member
        self.ctx = ctx
        self.text = Text().get()
        self.draw_background()
        self.draw_layout_map()
        self.img_draw = ImageDraw.Draw(self.img)
        
        self.draw_user_name()
        self.draw_badges()
        
        self.draw_command_stats()
        
        self.draw_progress_bar()
        self.draw_level_text()
        
        print(f'Generate image in {round(time() - s_time, 6)} seconds')
        return img_to_base64(self.img)
    
    def draw_layout_map(self):
        layout = Image.new('RGBA', (ProfileImage.width, ProfileImage.height))
        drawable_layout = ImageDraw.Draw(layout)
        drawable_layout.rounded_rectangle(
            Coords.nickname_block,
            radius=8,
            fill=(0, 0, 0)
        )
        drawable_layout.rounded_rectangle(
            Coords.badges_box,
            radius=8,
            fill=(0, 0, 0)
        )
        drawable_layout.rounded_rectangle(
            Coords.progressbar_box,
            radius=8,
            fill=(0, 0, 0)
        )
        drawable_layout.rounded_rectangle(
            Coords.command_stats_box,
            radius=8,
            fill=(0, 0, 0)
        )
        
        img_filter = ImageFilter.GaussianBlur(10)
        bg = self.img.copy()
        bg = ImageEnhance.Brightness(bg).enhance(self.opposite_bg_brightness)
        bg = bg.filter(img_filter)
        self.img.paste(bg, (0, 0), layout)
        
        
    def draw_command_stats(self) -> None:
        nums, commands, times = [], [], []
        for index, command in enumerate(self.member.profile.used_commands[::-1]):
            time = timedelta(
                seconds=datetime.now(pytz.utc).timestamp() - command.last_used.timestamp()
            ).total_seconds() // 60
            time = round(time)
            if time > 999:
                time = '> 999'
            
            if isinstance(time, int):
                time = str(time)
                
            nums.append(f'{index + 1}:')
            commands.append(command.name)
            times.append(f'{time}')

        counter = len(nums)
        if counter < 10:
            for count in range(counter, 11):
                nums.append(f'{count}:')
                commands.append('__N/A__')
                times.append('__N/A__')
            
        self.img_draw.text(
            Coords.command_stats_main_text,
            text=self.text.cmds.profile.items.last_commands,
            fill=Colors.l_grey,
            font=Fonts.roboto_medium,
            anchor='mt',
            align='center'
        )
        
        self.img_draw.text(
            Coords.commands_list_nums,
            text='\n'.join(nums),
            fill=Colors.l_grey,
            font=Fonts.roboto_mono.font_variant(size=21),
            anchor='la'
        )
        
        self.img_draw.text(
            Coords.commands_list_commands,
            text='\n'.join(commands),
            fill=Colors.l_grey,
            font=Fonts.roboto_mono.font_variant(size=21),
            anchor='ma',
            align='center'
        )
        
        self.img_draw.text(
            Coords.commands_list_times,
            text='\n'.join(times),
            fill=Colors.l_grey,
            font=Fonts.roboto_mono.font_variant(size=21),
            anchor='ra',
            align='right'
        )
        
        self.img_draw.text(
            Coords.command_stats_sub_text_num,
            text=self.text.cmds.profile.items.num,
            fill=Colors.l_grey,
            font=Fonts.roboto_medium.font_variant(size=15),
            anchor='lb',
            align='left'
        )
        
        self.img_draw.text(
            Coords.command_stats_sub_text_name,
            text=self.text.cmds.profile.items.command_name,
            fill=Colors.l_grey,
            font=Fonts.roboto_medium.font_variant(size=15),
            anchor='mb',
            align='center'
        )
                
        self.img_draw.text(
            Coords.command_stats_sub_text_time,
            text=self.text.cmds.profile.items.last_used_time,
            fill=Colors.l_grey,
            font=Fonts.roboto_medium.font_variant(size=15),
            anchor='rb',
            align='right'
        )
        
        self.img_draw.line(
            Coords.commands_stats_line,
            fill=self.img_opposite_color,
            width=2
        )
        
    def draw_user_name(self) -> None:
        text = f'{self.ctx.author.display_name}'
        self.img_draw.text(
            Coords.nickname_text,
            text=text,
            fill=Colors.l_grey,
            font=Fonts.roboto_25,
            anchor='ma'
        )
        
    def draw_badges(self) -> None:
        badges = ['dev', 'tester', 'beta_tester', 'administrator', 'docs_contributor', 'translator', 'theme_creator', 'active_user', 'streamer', 'premium', 'verified']
        all_badges_size = len(badges) * (Badges.badge_size[0] + Badges.badge_indent)
        canvas = Image.new('RGBA', (all_badges_size, Badges.badge_size[1]))
        offset = 0
        
        for badge in badges:
            canvas.paste(getattr(Badges, badge), (offset, 0))
            offset += Badges.badge_size[0] + Badges.badge_indent
            
        self.img_draw.text(
            Coords.badges_text,
            text=f'{self.text.cmds.profile.items.badges}',
            fill=Colors.l_grey,
            font=Fonts.roboto_medium,
            anchor='mt'
        )
        self.img.paste(canvas, (ProfileImage.width // 2 - all_badges_size // 2, Coords.badges_box[1] + 25), canvas)
        
    def draw_progress_bar(self) -> None:
        mask = Image.new('RGBA', (ProgressBar.width, ProgressBar.height))
        bar = mask.copy()
        drawable_bar = ImageDraw.Draw(bar)
        drawable_mask = ImageDraw.Draw(mask)
        drawable_mask.polygon(
            (
                0, mask.size[1],
                ProgressBar.h_offset, 0,
                mask.size[0], 0,
                mask.size[0] - ProgressBar.h_offset, mask.size[1]
            ),
            fill=(0, 0, 0),
            width=2
        )
        level = get_level(self.member.profile.level_exp)
        bar_fill = level.rem_exp / level.next_exp
        
        bar_width = int(ProgressBar.width * bar_fill)
        drawable_bar.rectangle(
            (0, 0, ProgressBar.width * bar_fill, ProgressBar.height),
            fill=self.img_opposite_color
        )
        drawable_bar.rectangle(
            (bar_width, 0, bar.size[0], bar.size[1]),
            fill=self.img_avg_color
        )
        bar_coords = (
            (ProfileImage.width - bar.size[0]) // 2, 
            ProgressBar.v_offset
        )
        
        self.img.paste(
            bar, 
            bar_coords, 
            mask
        )
        
    def draw_level_text(self) -> None:
        level = get_level(self.member.profile.level_exp)
        self.img_draw.text(
            Coords.progressbar_text_exp_rem,
            text=str(level.rem_exp),
            fill=Colors.l_grey,
            font=Fonts.roboto
        )
        self.img_draw.text(
            Coords.progressbar_text_exp_next,
            text=str(level.next_exp),
            fill=Colors.l_grey,
            font=Fonts.roboto,
            anchor='rt'
        )
        self.img_draw.text(
            (
                self.img.size[0] // 2, 
                ProgressBar.v_offset - ProgressBar.text_offset
            ),
            text=f'{self.text.cmds.profile.items.level} {level.level}',
            fill=Colors.l_grey,
            font=Fonts.roboto,
            anchor='mt'
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
        else:
            self.img = ProfileBackgrounds.gray
        
        self.img = self.img.convert('RGBA')
        avg_color_per_row = numpy.average(self.img, axis=0)
        img_avg_color = numpy.average(avg_color_per_row, axis=0)
        self.img_avg_color = (int(img_avg_color[0]), int(img_avg_color[1]), int(img_avg_color[2]))
        
        self.img_opposite_color = (
            255 - self.img_avg_color[0],
            255 - self.img_avg_color[1],
            255 - self.img_avg_color[2]
        )
        
        avg_color = int(numpy.average(self.img_avg_color))

        if avg_color < 30:
            self.opposite_bg_brightness = 4.0
        elif avg_color < 60:
            self.opposite_bg_brightness = 0.8
        else:
            self.opposite_bg_brightness = 0.5
