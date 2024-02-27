from typing import Literal

from discord import ButtonStyle, Interaction, File, InputTextStyle
from discord.ext import commands
from discord.ui import View, InputText, Modal, button

from lib.data_classes.db_player import ImageSettings
from lib.database.players import PlayersDB
from lib.embeds.info import InfoMSG
from lib.locale.locale import Text
from lib.settings.settings import Config

class Session:
    ...


class Modals:
    class ReportModal(Modal):
        def __init__(self, bot: commands.Bot, ctx: commands.Context, *args, **kwargs):
            super().__init__(title=Text().get().cmds.report.descr.sub_descr.title, *args, **kwargs)
            
            self.bot = bot
            self.ctx = ctx
            self.add_item(InputText(label=Text().get().cmds.report.descr.sub_descr.type_label, 
                                    placeholder=Text().get().cmds.report.descr.sub_descr.type_placeholder, max_length=1, required=False))
            self.add_item(InputText(label=Text().get().cmds.report.descr.sub_descr.label, 
                                    style=InputTextStyle.multiline, min_length=10, max_length=500,  
                                    placeholder=Text().get().cmds.report.descr.sub_descr.placeholder, 
                                    required=True))

        async def callback(self, interaction: Interaction):
            Text().load_from_context(self.ctx)

            rep_type = self.children[0].value
            rep_type = 'b' if not rep_type else rep_type.lower()
            if rep_type not in ['b', 's']:
                await interaction.response.send_message('👎', ephemeral=True)   #TODO не нравится - меняй
                return
            rep_data = self.children[1].value
            send_channel = self.bot.get_channel(getattr(Config().cfg.report, 
                                                        'bug_channel_id' if rep_type == 'b' else 'suggestion_channel_id'))
            await send_channel.send(f'```py\nfrom: {interaction.user.name}\ntype: {rep_type}\nid: {interaction.user.id}```\n' + rep_data.strip())
            await interaction.response.send_message(embed=self.inf_msg.custom(
                Text().get(),
                text=getattr(Text().get().cmds.report.info, "bug_report_send_ok" if rep_type == 'b' else 'suggestion_send_ok'),
                title=Text().get().frequent.info.info,
                colour='green'
            ))


class Buttons:
    async def save_callback(self, _, interaction: Interaction):
        Text().load_from_context(self.ctx)

        if self.check_user(interaction):
            await interaction.response.send_message(
                embed=self.inf_msg.not_button_owner(), ephemeral=True
                )
            return

        self.db.set_image_settings(interaction.user.id, self.current_settings)
        await interaction.response.send_message(embed=self.inf_msg.custom(
            Text().get(),
            text=Text().get().cmds.image_settings.info.set_ok,
            colour='green'
        ))
        await interaction.message.delete()
            
    async def cancel_callback(self, _, interaction: Interaction):
        Text().load_from_context(self.ctx)

        if self.check_user(interaction):
            await interaction.response.send_message(
                embed=self.inf_msg.not_button_owner(), ephemeral=True
                )
            return
                
        await interaction.response.send_message(
            embed=self.inf_msg.custom(
                Text().get(),
                Text().get().cmds.image_settings.info.canceled_settings_change,
                colour='green'
            )
        )
        await interaction.message.delete()
    
    async def update_callback(self, _, interaction: Interaction):
        Text().load_from_context(self.ctx)

        if self.cooldown.get_bucket(interaction.message).update_rate_limit():
            await interaction.response.send_message(
                embed=self.inf_msg.cooldown_not_expired()
            )
            return

        if self.check_user(interaction):
            await interaction.response.send_message(
                embed=self.inf_msg.not_button_owner(), ephemeral=True
                )
            return
                
        generate_res = await self.session_self._generate_image(self.ctx)
        if isinstance(generate_res, File):
            await interaction.response.send_message(file=generate_res, view=self)
        else:
            await interaction.response.send_message(embed=generate_res)


class ButtonBase(View):
    def __init__(self, bot: commands.Bot, ctx: commands.Context, *args, **kwargs):
        self.bot = bot
        self.ctx = ctx
        self.user_id = ctx.author.id
        super().__init__(*args, **kwargs)
    
    def check_user(self, interaction: Interaction):
        return self.user_id != interaction.user.id

    async def on_timeout(self):
        await self.message.edit(view=None)


class ViewMeta(type):
    timeout = {'session': 3600 * 24, 'image_settings': 3600 * 24, 'report': 3600 * 24}
    views = {'session': [Buttons.update_callback], 
             'image_settings': [Buttons.save_callback, Buttons.cancel_callback],
             'report': Modals.ReportModal}
    kwargs = {'session': {'update_callback': {'style': ButtonStyle.primary, 'row': 0}}, 
              'image_settings': {'save_callback': {'style': ButtonStyle.green, 'row': 0}, 
                                 'cancel_callback': {'style': ButtonStyle.red, 'row': 0}}}

    def __new__(cls, bot: commands, ctx: commands.Context, type: Literal['image_settings', 'session', 'report'], 
                session_self: Session=None, current_settings: ImageSettings=None):
        Text().load_from_context(ctx)

        if type in ['image_settings', 'session']:
            attrs = {}
            for view in cls.views[type]:
                view_name = view.__name__
                attrs[view_name] = button(label=cls._get_label(type)[view_name],
                                          **cls.kwargs[type][view_name])(view)
            new_cls = super().__new__(cls, f'View', (ButtonBase,), attrs)
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

        return cls_self

    def __init__(self, bot: commands.Bot, ctx: commands.Context, type: Literal['image_settings', 'session', 'suggestion'], 
                 session_self: Session=None, current_settings: ImageSettings=None):
        pass
    
    def _get_label(type: Literal['image_settings', 'session']) -> dict:
        if type == 'image_settings':
            return {'save_callback': '✔', 'cancel_callback': '❌'}
        elif type == 'session':
            return {'update_callback': Text().get().cmds.get_session.descr.sub_descr.button_update}
