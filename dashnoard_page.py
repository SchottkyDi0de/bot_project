from pywebio.output import *
from pywebio.input import *
import pywebio
from pywebio import start_server
from unittest import TestCase
    

pywebio.config(theme='dark', title='Dashboard Page')

class PageLayout:
    def __init__(self) -> None:
        pass
    
    def side_panel(self) -> pywebio.output.Output:
        return put_column([
            put_info(
                'Side Panel',
                position=OutputPosition.TOP
            ),
            put_scrollable([
                put_text('Main info'),
                put_text('Image Settings'),
                put_text('Session Settings'),
                put_text(''),
                ]),
            ], size='20% 80%')
    
    def dashboard_page(self):
        put_row([
            self.side_panel(),
            put_text('# Welcome to you personal dashboard', position=-1, inline=True),
            put_text('Account _Zener\nPlayer: RTX4080 | RU', position=-1)
        ], size='20% 55% 25%')

p = PageLayout()
start_server(p.dashboard_page, port=8080, debug=True)
