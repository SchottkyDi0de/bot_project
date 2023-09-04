'''
В этом модуле генерируются все Embed сообщения с учётом
настроек локализации
'''
from discord import Colour, Embed

from lib.locale.locale import Text


class CommonMSG():
    text = Text().get()
    
    help = Embed(
        title=text.help.help,
        description=text.help.common,
        colour=Colour.blurple()
    )

    def update_locale(self):
        self.text = Text().get()

