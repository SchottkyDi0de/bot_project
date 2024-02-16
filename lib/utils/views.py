from discord import ButtonStyle, Interaction, File
from discord.ext import commands
from discord.ui import View, button

from lib.data_classes.db_player import ImageSettings
from lib.database.players import PlayersDB
from lib.embeds.info import InfoMSG
from lib.locale.locale import Text
from lib.utils.singleton_factory import singleton


class ViewBase(View):
    def __init__(self, user_id: int, *args, **kwargs):
        self.user_id = user_id
        super().__init__(*args, **kwargs)
    
    def check_user(self, interaction: Interaction):
        return self.user_id != interaction.user.id

    async def on_timeout(self):
        await self.message.edit(view=None)


@singleton
class Views:
    def __init__(self):
        self.db = PlayersDB()
        self.inf_msg = InfoMSG()
    
    def get_image_settings_view(self, ctx: commands.Context, user_id: int, currecnt_settings: ImageSettings) -> View:
        class MyView(ViewBase):
            @button(label='✔', style=ButtonStyle.green, row=0)
            async def save_callback(view_self, _, interaction: Interaction):
                Text().load_from_context(ctx)

                if view_self.check_user(interaction):
                    await interaction.response.send_message(
                        embed=self.inf_msg.not_button_owner(), ephemeral=True
                        )
                    return

                self.db.set_image_settings(interaction.user.id, currecnt_settings)
                await interaction.response.send_message(embed=self.inf_msg.custom(
                    Text().get(),
                    text=Text().get().cmds.image_settings.info.set_ok,
                    colour='green'
                ))
                await interaction.message.delete()
            
            @button(label='❌', style=ButtonStyle.red, row=0)
            async def cancel_callback(view_self, _, interaction: Interaction):
                Text().load_from_context(ctx)

                if view_self.check_user(interaction):
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
        
        return MyView(user_id)

    def get_session_update_view(self, session_self, ctx: commands.Context, user_id: int) -> View:
        Text().load_from_context(ctx)

        class MyView(ViewBase):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)
            
            @button(label=Text().get().cmds.get_session.descr.sub_descr.button_update, 
                    style=ButtonStyle.primary, row=0)
            async def update_callback(view_self, _, interaction: Interaction):
                if view_self.cooldown.get_bucket(interaction.message).update_rate_limit():
                    await interaction.response.send_message(
                        embed=self.inf_msg.cooldown_not_expired()
                    )
                    return

                if view_self.check_user(interaction):
                    await interaction.response.send_message(
                        embed=self.inf_msg.not_button_owner(), ephemeral=True
                        )
                    return
                
                generate_res = await session_self._generate_image(ctx)
                if isinstance(generate_res, File):
                    await interaction.response.send_message(file=generate_res, view=view_self)
                else:
                    await interaction.response.send_message(embed=generate_res)
        
        return MyView(user_id, timeout=3600 * 24)
