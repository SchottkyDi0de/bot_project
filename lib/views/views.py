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

from lib.locale.locale import Text
from lib.views.buttons import Buttons
from lib.views.modals import ReportModal
from lib.views.select_menu import SelectMenu


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
        await self.message.edit(view=None)


class ViewMeta(type):
    timeout = {'session': 3600 * 24, 'image_settings': 3600 * 24, 'report': 3600 * 24,
               'replay': 3600}
    views = {'session': [Buttons.update_callback], 
             'image_settings': [Buttons.save_callback, Buttons.cancel_callback],
             'replay': SelectMenu.replay_select_callback,
             'report': ReportModal}
    kwargs = {'session': {'update_callback': {'style': ButtonStyle.gray, 'row': 0, "emoji": "🔄"}}, 
              'image_settings': {'save_callback': {'style': ButtonStyle.green, 'row': 0}, 
                                 'cancel_callback': {'style': ButtonStyle.red, 'row': 0}}}

    def __new__(cls, bot: commands.Bot, ctx: ApplicationContext, type: Literal['image_settings', 'session', 'replay', 'report'], 
                session_self: Session=None, current_settings: ImageSettings=None, report_type: Literal['b', 's']=None, replay_data: ParsedReplayData=None):
        Text().load_from_context(ctx)

        if type in ['image_settings', 'session']:
            attrs = {}
            for view in cls.views[type]:
                view_name = view.__name__
                attrs[view_name] = button(label=cls._get_label(type)[view_name],
                                          **cls.kwargs[type][view_name])(view)
            new_cls = super().__new__(cls, f'View', (ViewBase,), attrs)
        elif type in ["replay"]:
            option = []
            for player in sorted(replay_data.players, key=lambda x: x.info.nickname):
                option.append(SelectOption(label=player.info.nickname))
            new_cls = super().__new__(cls, f'View', (ViewBase,), {'replay_select_callback': select(options=option, max_values=1)(cls.views[type])})
        else:
            new_cls = cls.views[type]
        
        cls_self = new_cls(bot, ctx, timeout=cls.timeout[type])
        cls_self.db = PlayersDB()
        cls_self.inf_msg = InfoMSG()

        match type:
            case 'session':
                cls_self.session_self = session_self
                cls_self.cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)
            case 'image_settings':
                cls_self.current_settings = current_settings
            case 'report':
                cls_self.report_type = report_type
            case 'replay':
                cls_self.api = API()
                cls_self.sdb = ServersDB()
                cls_self.cache = Cache(ttl=3600)
                cls_self._build_global_data = SelectMenu._build_global_data
                cls_self.data = replay_data

        return cls_self

    def __init__(self, bot: commands.Bot, ctx: ApplicationContext, type: Literal['image_settings', 'session', 'replay', 'report'], 
                 session_self: Session=None, current_settings: ImageSettings=None, report_type: Literal['b', 's']=None, replay_data: ParsedReplayData=None):
        pass
    
    def _get_label(type: Literal['image_settings', 'session']) -> dict:
        if type == 'image_settings':
            return {'save_callback': '✔', 'cancel_callback': '❌'}
        elif type == 'session':
            return {'update_callback': Text().get().cmds.get_session.descr.sub_descr.button_update}