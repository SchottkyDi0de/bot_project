from typing import Literal

from discord import ButtonStyle, Interaction, File
from discord.ext import commands
from discord.ui import View, button

from lib.data_classes.db_player import ImageSettings
from lib.database.players import PlayersDB
from lib.embeds.info import InfoMSG
from lib.locale.locale import Text

class Session:
    ...


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
    
    async def update_callback(view_self, _, interaction: Interaction):
        Text().load_from_context(view_self.ctx)

        if view_self.cooldown.get_bucket(interaction.message).update_rate_limit():
            await interaction.response.send_message(
                embed=view_self.inf_msg.cooldown_not_expired()
            )
            return

        if view_self.check_user(interaction):
            await interaction.response.send_message(
                embed=view_self.inf_msg.not_button_owner(), ephemeral=True
                )
            return
                
        generate_res = await view_self.session_self._generate_image(view_self.ctx)
        if isinstance(generate_res, File):
            await interaction.response.send_message(file=generate_res, view=view_self)
        else:
            await interaction.response.send_message(embed=generate_res)


class ViewBase(View):
    def __init__(self, ctx: commands.Context, *args, **kwargs):
        self.ctx = ctx
        self.user_id = ctx.author.id
        super().__init__(*args, **kwargs)
    
    def check_user(self, interaction: Interaction):
        return self.user_id != interaction.user.id

    async def on_timeout(self):
        await self.message.edit(view=None)


class ViewMeta(type):
    timeout = {'session': 3600 * 24, 'image_settings': 3600 * 24}
    buttons = {'session': [Buttons.update_callback], 
               'image_settings': [Buttons.save_callback, Buttons.cancel_callback]}
    kwargs = {'session': {'update_callback': {'style': ButtonStyle.primary, 'row': 0}}, 
              'image_settings': {'save_callback': {'style': ButtonStyle.green, 'row': 0}, 
                                 'cancel_callback': {'style': ButtonStyle.red, 'row': 0}}}

    def __new__(cls, ctx: commands.Context, _type: Literal['image_settings', 'session'], 
                sesion_self: Session=None, current_settings: ImageSettings=None):
        Text().load_from_context(ctx)

        attrs = {}
        for button_func in cls.buttons[_type]:
            func_name = button_func.__name__
            attrs[func_name] = button(label=cls._get_label(_type)[func_name],
                                       **cls.kwargs[_type][func_name])(button_func)
        new_cls = type(f'View', (ViewBase,), attrs)
        cls_self = new_cls(ctx, timeout=cls.timeout[_type])
        cls_self.db = PlayersDB()
        cls_self.inf_msg = InfoMSG()

        match _type:
            case 'session':
                cls_self.session_self = sesion_self
                cls_self.cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)
            case 'image_settings':
                cls_self.current_settings = current_settings

        return cls_self

    def __init__(self, ctx: commands.Context, _type: Literal['image_settings', 'session'], 
                 sesion_self: Session=None, current_settings: ImageSettings=None):
        pass
    
    def _get_label(type: Literal['image_settings', 'session']) -> dict:
        if type == 'image_settings':
            return {'save_callback': '✔', 'cancel_callback': '❌'}
        elif type == 'session':
            return {'update_callback': Text().get().cmds.get_session.descr.sub_descr.button_update}
