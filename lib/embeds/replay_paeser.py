
from discord import Embed

from lib.locale.locale import Text
from lib.data_classes.replay import CommonReplayData


class ReplayParserEmbeds():
    def __init__(self, data: CommonReplayData):
        self.data = data
        self.embed = None

    def build_embed(self) -> Embed:
        self.embed = Embed(
            title=''
        )