from discord import Interaction, InputTextStyle
from discord.ui import Modal, InputText
from discord.commands import ApplicationContext
from discord.ext import commands

from lib.locale.locale import Text
from lib.settings.settings import Config


class ReportModal(Modal):
    report_type2text = {"b": "bug_report", "s": "suggestion"}
    def __init__(self, bot: commands.Bot, ctx: ApplicationContext, *args, **kwargs):
        super().__init__(title=Text().get().cmds.report.descr.sub_descr.title, *args, **kwargs)
            
        self.bot = bot
        self.ctx = ctx
        self.add_item(InputText(label=Text().get().cmds.report.descr.sub_descr.label, 
                                style=InputTextStyle.multiline, min_length=10, max_length=500,  
                                placeholder=Text().get().cmds.report.descr.sub_descr.placeholder, 
                                required=True))

    async def callback(self, interaction: Interaction):
        await Text().load_from_context(self.ctx)

        rep_type = self.report_type
        rep_data = self.children[0].value
        send_channel = self.bot.get_channel(getattr(Config().cfg.report, 
                                                        'bug_channel_id' if rep_type == 'b' else 'suggestion_channel_id'))
        await send_channel.send(f'```py\nfrom: {interaction.user.name}\ntype: {self.report_type2text[rep_type]}\nid: {interaction.user.id}```\n' + rep_data.strip())
        await interaction.response.send_message(embed=self.inf_msg.custom(
            Text().get(),
            text=getattr(Text().get().cmds.report.info, "bug_report_send_ok" if rep_type == 'b' else 'suggestion_send_ok'),
            title=Text().get().frequent.info.info,
            colour='green'
        ))
        
    async def on_timeout(self):
        await self.ctx.message.delete()