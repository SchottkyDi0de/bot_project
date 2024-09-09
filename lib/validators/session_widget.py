from re import Match

from lib.image.utils.color_validator import CompiledRegex

from lib.locale.locale import Text

from .base import Validator


class MaxStatsBlocks(Validator):
    min = 1
    max = 3


class MaxStatsSmallBlocks(Validator):
    min = 0
    max = 2


class UpdateTime(Validator):
    min = 30
    max = 360
    

class BackgroundTransparency(Validator):
    min = 0
    max = 100

    def post_procces(self):
        return self.data / 100


class StatsBlockColor(Validator):
    rgb_match: Match | None
    hex_match: Match | None

    @property
    def limits(self):
        return Text().get().cmds.settings.sub_descr.validators.session_widget.stats_block_color
    
    def validate(self):
        self.rgb_match = CompiledRegex.rgb.match(self.data)
        self.hex_match = CompiledRegex.hex.match(self.data)
        if self.rgb_match is None and self.hex_match is None:
            return False
        return True
    
    def post_procces(self) -> str:
        if self.hex_match is not None:
            return self.data
        data = tuple(int(i) for i in self.rgb_match.groups())
        return f"#{data[0]:02x}{data[1]:02x}{data[2]:02x}"
