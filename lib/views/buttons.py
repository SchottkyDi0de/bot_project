from discord import Interaction, File

from lib.locale.locale import Text


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
                embed=self.inf_msg.cooldown_not_expired(), ephemeral=True
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
            await interaction.message.delete()
        else:
            await interaction.response.send_message(embed=generate_res)