'''
В этом модуле генерируются все Embed сообщения с учётом
настроек локализации
'''
from discord import Colour, Embed

from lib.locale import locale


class CommonMSG():
    text = locale.Text()
    help = Embed(
        title=text.data.help.help,
        description=text.data.help.common,
        colour=Colour.blurple()
    )



