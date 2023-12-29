'''
В этом модуле генерируются все Embed сообщения с учётом
настроек локализации
'''
from discord import Colour, Embed

from lib.locale.locale import Text


# class CommonMSG():
#     def __init__(self):
#         text = Text().get()
        
#         self.help = Embed(
#             title=text.help.help,
#             description=text.help.common,
#             colour=Colour.blurple()
#         )
