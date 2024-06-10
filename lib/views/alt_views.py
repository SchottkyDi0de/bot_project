
import asyncio
from datetime import datetime, timedelta

from discord import ApplicationContext, ButtonStyle, Interaction, File, SelectOption
from discord.ext import commands
from lib.data_classes.db_server import DBServer
from lib.data_parser.parse_data import get_session_stats
from discord import ui
import pytz

from lib.api.async_wotb_api import API
from lib.data_classes.locale_struct import Localization
from lib.data_classes.db_player import AccountSlotsEnum, GameAccount, ImageSettings, SessionSettings
from lib.database.players import PlayersDB
from lib.embeds.info import InfoMSG
from lib.embeds.errors import ErrorMSG
from lib.error_handler.interactions import hook_exceptions
from lib.image.session import ImageGenSession
from lib.logger.logger import get_logger
from lib.utils.standard_account_validate import standard_account_validate
from lib.utils.slot_info import get_formatted_slot_info
from lib.locale.locale import Text
from lib.utils.string_parser import insert_data


_log = get_logger(__file__, 'AltViewsLogger', 'logs/alt_views.log')

class StartSession():
    def __init__(self, text: Localization, player_id: int, slot: AccountSlotsEnum, game_account: GameAccount) -> ui.View:
        class StartSessionView(ui.View):
            @ui.button(
                label=text.cmds.start_autosession.descr.this,
                style=ButtonStyle.success,
                emoji='✅'
            )
            async def accept_button(self, button: ui.Button, interaction: Interaction):
                @hook_exceptions(interaction=interaction, logger=_log)
                async def button_callback():
                    if interaction.user.id != player_id:
                        await interaction.response.send_message(
                            embed=ErrorMSG().custom(
                                locale=text,
                                text=text.views.not_owner
                            ),
                            ephemeral=True
                        )
                        return
                    
                    session_settings = SessionSettings().model_validate({})
                    session_settings.time_to_restart = datetime.now(pytz.utc) + timedelta(days=1)
                    session_settings.is_autosession = True
                    await PlayersDB().start_session(
                        slot=slot,
                        member_id=player_id,
                        last_stats=await API().get_stats(
                            region=game_account.region,
                            game_id=game_account.game_id
                        ),
                        session_settings=session_settings,
                    )

                    await interaction.message.edit(view=None) 
                    await interaction.response.send_message(
                        embed=InfoMSG().custom(
                            locale=text,
                            text=text.cmds.start_autosession.info.started,
                            colour='green'
                        ),
                    )
                    
                await button_callback()

        self.view = StartSessionView(disable_on_timeout=True)
        
    def get_view(self):
        return self.view
    
    
class SlotOverride:
    def __init__(self, text: Localization, game_account: GameAccount, player_id: int, slot: AccountSlotsEnum) -> ui.View:
        class SlotOverrideView(ui.View):
            @ui.button(
                label=text.frequent.common.yes,
                style=ButtonStyle.green,
                emoji='✔️'
            )
            async def button_accept(self, button: ui.Button, interaction: Interaction):
                @hook_exceptions(interaction=interaction, logger=_log)
                async def accept_button_callback():
                    if interaction.user.id != player_id:
                        await interaction.response.send_message(
                            embed=ErrorMSG().custom(
                                locale=text,
                                text=text.views.not_owner,
                            ),
                            ephemeral=True
                        )
                        return
                    await PlayersDB().set_member(
                        slot=slot,
                        member_id=player_id,
                        game_account=game_account,
                        slot_override=True
                    )
                    await interaction.message.edit(view=None)
                    await interaction.response.send_message(
                        embed=InfoMSG().custom(
                            locale=text,
                            colour='green',
                            text=text.cmds.set_player.info.set_player_ok
                        ),
                        view=StartSession(text=text, player_id=player_id, slot=slot, game_account=game_account).get_view()
                    )
                
                await accept_button_callback()

            @ui.button(
                label=text.frequent.common.no,
                style=ButtonStyle.red,
                emoji='✖️'
            )
            async def button_decline(self, button: ui.Button, interaction: Interaction):
                @hook_exceptions(interaction=interaction, logger=_log)
                async def decline_button_callback():
                    if interaction.user.id != player_id:
                        await interaction.response.send_message(
                            embed=ErrorMSG().custom(
                                locale=text,
                                text=text.views.not_owner
                            ),
                            ephemeral=True
                        )
                        return
                    await interaction.message.edit(view=None)
                    await interaction.response.send_message(
                        embed=InfoMSG().custom(
                            locale=text,
                            colour='red',
                            text=text.frequent.info.discard_changes,
                            title=text.frequent.info.warning
                        ),
                    )

                await decline_button_callback()
                
        self.view = SlotOverrideView(disable_on_timeout=True)
    
    def get_view(self) -> ui.View:
        return self.view
    
            
class DeleteAccountConfirmation:
    def __init__(self, text: Localization, player_id: int) -> ui.View:
        class DeleteAccountConfirmationView(ui.View):
            @ui.button(
                label=text.frequent.common.yes,
                style=ButtonStyle.red,
                emoji='✔️'
            )
            async def button_accept(self, button: ui.Button, interaction: Interaction):
                @hook_exceptions(interaction=interaction, logger=_log)
                async def accept_button_callback():
                    if interaction.user.id != player_id:
                        await interaction.response.send_message(
                            embed=ErrorMSG().custom(
                                locale=text,
                                text=text.views.not_owner
                            ),
                            ephemeral=True
                        )
                        return
                    
                    await PlayersDB().delete_member(player_id)
                    await interaction.message.edit(view=None)
                    await interaction.response.send_message(
                        embed=InfoMSG().custom(
                            locale=text,
                            colour='green',
                            text=text.cmds.delete_player.info.success
                        ),
                    )
                    
                await accept_button_callback()
                    
            @ui.button(
                label=text.frequent.common.no,
                style=ButtonStyle.green,
                emoji='✖️'
            )
            async def button_decline(self, button: ui.Button, interaction: Interaction):
                @hook_exceptions(interaction=interaction, logger=_log)
                async def decline_button_callback():
                    if interaction.user.id != player_id:
                        await interaction.response.send_message(
                            embed=ErrorMSG().custom(
                                locale=text,
                                text=text.views.not_owner
                            ),
                            ephemeral=True
                        )
                        return
                    
                    await interaction.message.edit(view=None)
                    await interaction.response.send_message(
                        embed=InfoMSG().custom(
                            locale=text,
                            colour='red',
                            text=text.frequent.info.discard_changes,
                            title=text.frequent.info.warning
                        ),
                    )
                
                await decline_button_callback()
                
        self.view = DeleteAccountConfirmationView(disable_on_timeout=True)

    def get_view(self):
        return self.view


class UpdateSession:
    def __init__(self, game_account: GameAccount, player_id: int, slot: AccountSlotsEnum, server: DBServer | None, text: Localization) -> ui.View:
        class UpdateSessionView(ui.View):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)
                
            @ui.button(
                label=text.cmds.get_session.descr.sub_descr.button_update,
                style=ButtonStyle.blurple,
                emoji='🔁'
            )
            async def update_session(self, button: ui.Button, interaction: Interaction):
                await Text().load_from_interaction(interaction)
                text = Text().get()
                
                @hook_exceptions(interaction=interaction, logger=_log)
                async def update_session_callback():
                    bucket = self.cooldown.get_bucket(interaction.message)
                    cooldown_expired = bucket.update_rate_limit()

                    if cooldown_expired:
                        raise commands.CommandOnCooldown(self.cooldown, cooldown_expired, commands.BucketType.user)
                    
                    if interaction.user.id != player_id:
                        await interaction.response.send_message(
                            embed=ErrorMSG().custom(
                                locale=text,
                                text=text.views.not_owner
                            ),
                            ephemeral=True
                        )
                        return
                    
                    game_account, member, account_slot = await standard_account_validate(account_id=player_id, slot=slot)
                    
                    stats = await API().get_stats(
                        region=game_account.region,
                        game_id=game_account.game_id
                    )
                    diff_data = get_session_stats(game_account.last_stats, stats)
                    
                    await interaction.response.defer()
                    image = ImageGenSession().generate(
                        data=stats,
                        diff_data=diff_data,
                        player=member,
                        server=server,
                        slot=account_slot
                    )
                    
                    await interaction.edit_original_response(
                        embed=InfoMSG().custom(
                            locale=text,
                            colour='green',
                            text=get_formatted_slot_info(
                                slot=account_slot, 
                                text=text, 
                                game_account=game_account,
                                shorted=True
                            ),
                            fields=[
                                {
                                    'name': text.frequent.info.updated_at, 
                                    'value': f'<t:{int(datetime.now(pytz.utc).timestamp())}:R>'
                                }
                            ]
                        ),
                        files=[File(image, 'session.png')],
                    )
                    image.close()
                    
                await update_session_callback()
                
        self.view = UpdateSessionView(timeout=14_400, disable_on_timeout=True)
                
    def get_view(self) -> ui.View:
        return self.view


class StatsPreview:
    def __init__(self, player_id: int, slot: AccountSlotsEnum, text: Localization, image_settings: ImageSettings):
        class StatsPreviewView(ui.View):
            @ui.button(
                label=text.frequent.common.yes,
                style=ButtonStyle.green,
                emoji='✔️'
            )
            async def button_accept(self, button: ui.Button, interaction: Interaction):
                @hook_exceptions(interaction=interaction, logger=_log)
                async def accept_button_callback():
                    if interaction.user.id != player_id:
                        await interaction.response.send_message(
                            embed=ErrorMSG().custom(
                                locale=text,
                                text=text.views.not_owner
                            ),
                            ephemeral=True
                        )
                        return
                    
                    await PlayersDB().set_image_settings(slot=slot, member_id=player_id, settings=image_settings)
                    await interaction.response.edit_message(
                        view=None,
                        attachments=[],
                        embed=InfoMSG().custom(
                            locale=text,
                            colour='green',
                            text=text.cmds.image_settings.info.set_ok
                        ),
                    )
                    
                await accept_button_callback()
            
            @ui.button(
                label=text.frequent.common.no,
                style=ButtonStyle.red,
                emoji='✖️'
            )
            async def button_decline(self, button: ui.Button, interaction: Interaction):
                @hook_exceptions(interaction=interaction, logger=_log)
                async def decline_button_callback():
                    if interaction.user.id != player_id:
                        await interaction.response.send_message(
                            embed=ErrorMSG().custom(
                                locale=text,
                                text=text.views.not_owner
                            ),
                            ephemeral=True
                        )
                        return
                    await interaction.response.edit_message(
                        view=None,
                        attachments=[],
                        embed=InfoMSG().custom(
                            locale=text,
                            colour='orange',
                            text=text.cmds.image_settings.info.canceled_settings_change,
                            title=text.frequent.info.warning
                        )
                    )
                    
                await decline_button_callback()
                
        self.view = StatsPreviewView(disable_on_timeout=True)
        

class SwitchAccount:
    def __init__(self, text: Localization, member: DBServer, choices: list[SelectOption], slot: AccountSlotsEnum):
            
        class SwitchAccountView(ui.View):
            @ui.select(
                placeholder=text.cmds.switch_account.descr.this,
                options=choices,
            )
            async def select(self, select: ui.Select, interaction: Interaction):
                @hook_exceptions(interaction=interaction, logger=_log)
                async def select_callback():
                    if interaction.user.id != member.id:
                        await interaction.response.send_message(
                            embed=ErrorMSG().custom(
                                locale=text,
                                text=text.views.not_owner
                            ),
                            ephemeral=True
                        )
                        return
                    
                    
                    
                    embed = InfoMSG().custom(
                        locale=text,
                        text=insert_data(
                            text.cmds.switch_account.info.success,
                            {
                                'old_account' : get_formatted_slot_info(
                                    slot=slot,
                                    text=text,
                                    game_account=await PlayersDB().get_game_account(slot=slot, member=member),
                                    shorted=True
                                ),
                                'new_account' : get_formatted_slot_info(
                                    slot=AccountSlotsEnum[select.values[0]],
                                    text=text,
                                    game_account=await PlayersDB().get_game_account(slot=AccountSlotsEnum[select.values[0]], member=member),
                                    shorted=True
                                )
                            }
                        ),
                        colour='green'
                    )
                    await interaction.response.edit_message(
                        view=None,
                        embed=embed
                    )
                    
                    await PlayersDB().set_current_account(member_id=member.id, slot=AccountSlotsEnum[select.values[0]])
                    
                await select_callback()
                
        self.view = SwitchAccountView()
        
    def get_view(self) -> ui.View:
        return self.view