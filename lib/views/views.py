from typing import Literal

from discord import ButtonStyle, Interaction, SelectOption
from discord.commands import ApplicationContext
from discord.ext import commands
from discord.ui import View, button, select
from cacheout import Cache

from lib.api.async_wotb_api import API
from lib.data_classes.db_player import ImageSettings
from lib.data_classes.replay_data_parsed import ParsedReplayData
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.embeds.info import InfoMSG
from lib.locale.locale import Text
from lib.logger.logger import get_logger

from lib.views.buttons import Buttons
from lib.views.modals import ReportModal
from lib.views.select_menu import SelectMenu

_log = get_logger(__file__, 'ViewsLogger', 'logs/views.log')


class Session:
    ...


class ViewBase(View):
    def __init__(self, bot: commands.Bot, ctx: ApplicationContext, *args, **kwargs):
        self.bot = bot
        self.ctx = ctx
        self.user_id = ctx.author.id
        super().__init__(*args, **kwargs)
    
    def check_user(self, interaction: Interaction):
        return self.user_id != interaction.user.id

    async def on_timeout(self):
        ...


class BaseClass:
    def __class_getitem__(cls, item):
        return getattr(cls, item)


class TimeLimits(BaseClass):
    session = 3600
    image_settings = 3600
    report = 3600
    replay = 3600
    cooldowns = {"session": 10, "image_settings": 10, "report": 1800, "replay": 10}


class Views(BaseClass):
    session = [Buttons.update_callback]
    image_settings = [Buttons.save_callback, Buttons.cancel_callback]
    replay = SelectMenu.replay_select_callback
    report = ReportModal


class KeyWordArgs(BaseClass):
    session = {'update_callback': {'style': ButtonStyle.gray, 'row': 0, "emoji": "🔄"}}
    image_settings = {'save_callback': {'style': ButtonStyle.green, 'row': 0},
                      'cancel_callback': {'style': ButtonStyle.red, 'row': 0}}


class InitObject:
    type2attrs = {
        'session': ["session_self", "cooldown"],
        "image_settings": ["current_settings"],
        "report": ["report_type"],
        "replay": ["data", "api", "cache"]
        }

    def __class_getitem__(cls, item):
        cls_self = item["cls_self"]
        type = item["type"]
        cls._extend_needs_vars(type, item)

        cls_self.db = PlayersDB()
        cls_self.inf_msg = InfoMSG()
        cls_self.sdb = ServersDB()

        for attr in cls.type2attrs[type]:
            setattr(cls_self, attr, item[attr])
    
    def _extend_needs_vars(type: str, item: dict):
        dct = {
            "api": API(),
            "cooldown": commands.CooldownMapping.from_cooldown(1,  TimeLimits.cooldowns[type],
                                                               commands.BucketType.user),

            }
        if type == "replay":
            dct |= {"data": item['replay_data'],
                    "cache": Cache(ttl=3600)}
        item |= dct


class ViewMeta(type):
    def __new__(cls, bot: commands.Bot, ctx: ApplicationContext, type: Literal['image_settings', 'session', 'replay', 'report'], *,
                session_self: Session=None, current_settings: ImageSettings=None, report_type: Literal['b', 's']=None, replay_data: ParsedReplayData=None):
        # Text().load_from_context(ctx)
        _log.debug(f"Starting building view for {type}")

        if type in ['image_settings', 'session']:
            attrs = {}
            for view in Views[type]:
                view_name = view.__name__
                attrs[view_name] = button(label=cls._get_label(type)[view_name],
                                          **KeyWordArgs[type][view_name])(view)
            new_cls = super().__new__(cls, f'View', (ViewBase,), attrs)
        elif type in ["replay"]:
            option = []
            for player in sorted(replay_data.players, key=lambda x: x.info.nickname):
                option.append(SelectOption(label=player.info.nickname))
            new_cls = super().__new__(cls, f'View', (ViewBase,), {'replay_select_callback': select(options=option, max_values=1)(Views[type])})
        else:
            new_cls = Views[type]
        
        cls_self = new_cls(bot, ctx, timeout=TimeLimits[type])
        
        InitObject[locals()]

        return cls_self

    def __init__(self, bot: commands.Bot, ctx: ApplicationContext, type: Literal['image_settings', 'session', 'replay', 'report'], 
                 session_self: Session=None, current_settings: ImageSettings=None, report_type: Literal['b', 's']=None, replay_data: ParsedReplayData=None):
        pass
    
    def _get_label(type: Literal['image_settings', 'session']) -> dict:
        if type == 'image_settings':
            return {'save_callback': '✔', 'cancel_callback': '❌'}
        elif type == 'session':
            return {'update_callback': Text().get().cmds.get_session.descr.sub_descr.button_update}