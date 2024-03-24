from discord import Interaction, File

from lib.locale.locale import Text
from lib.logger.logger import get_logger

_log = get_logger(__file__, 'ButtonsLogger', 'logs/buttons.log')


class Buttons:
    async def save_callback(self, _, interaction: Interaction):
        Text().load_from_context(self.ctx)

        if self.check_user(interaction):
            await interaction.response.send_message(
                embed=self.inf_msg.not_button_owner(), ephemeral=True
                )
            return

        _log.debug(f"set image settings for {interaction.user.id}")
        self.db.set_image_settings(interaction.user.id, self.current_settings)

        await interaction.message.delete()

        await self.ctx.channel.send(embed=self.inf_msg.custom(
            Text().get(),
            text=Text().get().cmds.image_settings.info.set_ok,
            colour='green'
        ))
            
    async def cancel_callback(self, _, interaction: Interaction):
        Text().load_from_context(self.ctx)

        if self.check_user(interaction):
            await interaction.response.send_message(
                embed=self.inf_msg.not_button_owner(), ephemeral=True
                )
            return
        
        
        await interaction.message.delete()

        await self.ctx.channel.send(
            embed=self.inf_msg.custom(
                Text().get(),
                Text().get().cmds.image_settings.info.canceled_settings_change,
                colour='green'
            )
        )
    
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
        
        _log.debug(f"update session for {interaction.user.id}")
        generate_res = await self.session_self._generate_image(self.ctx)
        if isinstance(generate_res, File):
            await interaction.message.delete()
            await self.ctx.channel.send(file=generate_res, view=self)
        else:
            await interaction.response.send_message(embed=generate_res)