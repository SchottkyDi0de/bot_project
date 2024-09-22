from typing import TYPE_CHECKING

from aiogram.types import InputMediaPhoto, BufferedInputFile

from lib.image.settings_represent import SettingsRepresent
from lib.utils.string_parser import insert_data

from lib.database.players import PlayersDB
from lib.database.tankopedia import TankopediaDB
from lib.locale.locale import Text
from lib.buttons import Buttons
from lib.utils import jsonify, safe_divide

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message, User
    from aiogram.fsm.context import FSMContext
    
    from lib.data_classes.db_player import DBPlayer
    from lib.data_classes.locale_struct import Localization
    from lib.data_classes.api.player_stats import Statistics
    from lib.data_classes.replay_data_parsed import ParsedReplayData, PlayerResult
    from lib.data_classes.state_data import ImageSettingsStateData, WidgetSettingsStateData, SessionStateData


class ReplayParseSupport:
    _tankinfo_plug = type("tankinfo_plug", (), {"name": 'Unknown', "tier": '?'})

    @staticmethod
    def num_cutter(value: int) -> str:
        if value > 99_999:
            return str(round(value / 1000, 2)) + 'k'
        else:
            return str(value)

    @staticmethod
    def avg_stats_counter(data: 'ParsedReplayData', enemies: bool, locale: 'Localization') -> str:
        team = data.author.team_number
        avg_stats: str = ''
        avg_battles = 0
        avg_winrate = 0.0
        player_stats: 'list[Statistics]' = []

        for player in data.player_results:
            if enemies:
                if player.player_info.team != team:
                    if player.statistics:
                        player_stats.append(player.statistics)
            else:
                if player.player_info.team == team:
                    if player.statistics:
                        player_stats.append(player.statistics)

        if len(player_stats) > 0:
            avg_battles = round(sum(statistics.all.battles for statistics in player_stats) / len(player_stats))
            avg_winrate = round(sum(statistics.all.winrate for statistics in player_stats) / len(player_stats), 1)
        
        avg_stats = (
            format(
                locale.cmds.parse_replay.items.avg_stats[:15] + \
                    ('..' * (len(locale.cmds.parse_replay.items.avg_stats) > 15)),
                " <19"
            )+\
            format(
                str(avg_winrate),
                " <5"
            )+\
            ReplayParseSupport.num_cutter(avg_battles)+'\n'+('.'*29)+'\n'
        )
        return avg_stats
    
    @staticmethod
    def gen_players_list(data: 'ParsedReplayData', enemies: bool) -> str:
        team = data.author.team_number
        players: 'list[PlayerResult]' = []
        players_str = ''

        for player in data.player_results:
            if enemies:
                if player.player_info.team != team:
                    players.append(player)
            else:
                if player.player_info.team == team:
                    players.append(player)

        for enemy in players:
            if enemy.statistics:
                nickname = format(
                    enemy.player_info.nickname[:15] + ('..' * (len(enemy.player_info.nickname) > 15)),
                    " <19")
                winrate = format(
                    str(round(enemy.statistics.all.winrate, 1)),
                    " <5"
                )
                battles = ReplayParseSupport.num_cutter(enemy.statistics.all.battles)
                players_str += f'{nickname}{winrate}{battles}\n'
            else:
                players_str += f'{Text().get().cmds.parse_replay.items.empty_player}\n'
        
        return players_str

    @staticmethod
    async def get_text_by_player(player: 'PlayerResult', region: str):

        player_tank = await TankopediaDB().get_tank_by_id(player.info.tank_id, region=region)
                            
        accuracy = safe_divide(player.info.n_hits_dealt, player.info.n_shots) * 100
        pen_percent = safe_divide(player.info.n_penetrations_dealt, player.info.n_shots) * 100
                    
        text = insert_data(
                           Text().get().cmds.parse_replay.items.formenu,
                           {
                                'tank_name' : player_tank.name if player_tank is not None else 'Unknown',
                                'damage' : player.info.damage_dealt,
                                'spotted' : player.info.damage_assisted_1,
                                'xp' : player.info.base_xp,
                                'frags' : player.info.n_enemies_destroyed,
                                'blocked' : player.info.damage_blocked,
                                'shots' : player.info.n_shots,
                                'shots_hit' : player.info.n_hits_dealt,
                                'shots_penetrated' : player.info.n_penetrations_dealt,
                                'accuracy' : f'{accuracy:.2f}%',
                                'penetration_ratio' : f'{pen_percent:.2f}%',
                            }
                        )
        return text


class Functions:
    @staticmethod
    async def image_settings_other_back(msg: 'Message'):
        await msg.edit_text(text=Text().get().cmds.image_settings.sub_descr.choose_param2change,
                            reply_markup=Buttons.image_settings_other_buttons().get_keyboard(None))
    
    @staticmethod
    async def image_settings_back(bot: 'Bot', state: 'FSMContext', msg: 'Message | None'=None):
        await state.set_state()
        state_data: 'ImageSettingsStateData' = (await state.get_data())["data"]
        if msg:
            await msg.delete()
        main_message: 'Message' = state_data.main_message
        await state_data.stats_preview.update_preview(bot, state)
        await main_message.edit_media(InputMediaPhoto(media=BufferedInputFile(SettingsRepresent().draw(
                                                                               state_data.current_image_settings).read(), 
                                                                              'settings_represent.png')))
        await main_message.edit_caption(caption=Text().get().cmds.image_settings.sub_descr.main_text,
                                        reply_markup=Buttons.image_settings_buttons(state_data).get_keyboard(1))
    
    @staticmethod
    async def session_widget_back(message: 'Message', state: 'FSMContext'):
        await state.set_state()

        state_data: 'WidgetSettingsStateData' = (await state.get_data())["data"]
        await message.edit_text(
            text=insert_data(Text().get().cmds.session_widget.settings.descr,
                                {"settings": jsonify(Text().get().cmds.session_widget.settings.buttons.edit_buttons, 
                                                     state_data.current_widget_settings.model_dump())}),
            reply_markup=Buttons.session_widget_settings_buttons(state_data).get_keyboard(1),
            parse_mode="MarkdownV2"
            )
    
    @staticmethod
    async def new_hook(msg: 'Message', state: 'FSMContext', member: 'DBPlayer | None'=None):
        if member is None:
            member = await PlayersDB().get_member(msg.from_user.id)

        await state.update_data({"data": member.hook_stats})

        await msg.reply(text=Text().get().cmds.hook.sub_descr.choose_target_region,
                        reply_markup=Buttons.hook_region_buttons().get_keyboard(4))
        

    @staticmethod
    async def parse_replay_main_message(msg: 'Message', from_user: 'User', replay_data: 'ParsedReplayData', region: str):
        locale = Text().get()
        author_id = replay_data.author.account_id
        tankinfo = await TankopediaDB().get_tank_by_id(replay_data.author.tank_id, region)
        tank = tankinfo if tankinfo is not None else ReplayParseSupport._tankinfo_plug

        for player_result in replay_data.player_results:
            if player_result.info.account_id == author_id:
                author_stats = player_result
                break
        else:
            return

        text = insert_data(locale.cmds.parse_replay.items.title,
                           {"member_name": from_user.first_name,
                            "nickname": author_stats.player_info.nickname}) + '\n'

        text = insert_data(
                locale.cmds.parse_replay.items.description,
                {
                    'battle_result'     :   locale.cmds.parse_replay.items.common.win if replay_data.author.winner is True
                                                else locale.cmds.parse_replay.items.common.lose if replay_data.author.winner is False else \
                                                    locale.cmds.parse_replay.items.common.draw,
                    'battle_type'       :   getattr(locale.gamemodes, replay_data.room_name, locale.gamemodes.unknown),
                    'tank_name'         :   tank.name,
                    'tier'              :   tank.tier,
                    'map'               :   getattr(locale.map_names, replay_data.map_name, locale.map_names.unknown),
                    'time'              :   str(replay_data.time_string),
                    'damage_dealt'      :   str(author_stats.info.damage_dealt),
                    'damage_assisted'   :   str(author_stats.info.damage_assisted_1),
                    'damage_blocked'    :   str(author_stats.info.damage_blocked),
                    'point_captured'    :   str(author_stats.info.victory_points_earned),
                    'point_defended'    :   str(author_stats.info.victory_points_seized),
                    'shots_fired'       :   str(author_stats.info.n_shots),
                    'shots_hit'         :   str(author_stats.info.n_hits_dealt),
                    'shots_penetrated'  :   str(author_stats.info.n_penetrations_dealt),
                    'accuracy'          :   str(round(replay_data.author.accuracy, 2)),
                    'penetration'       :   str(round(replay_data.author.penetrations_percent, 2)),
                    'allies'            :   ReplayParseSupport.avg_stats_counter(replay_data, False, locale) + \
                                                ReplayParseSupport.gen_players_list(replay_data, False),
                    'enemies'           :   ReplayParseSupport.avg_stats_counter(replay_data, True, locale) + \
                                                ReplayParseSupport.gen_players_list(replay_data, True)
                }
            )
    
        await msg.edit_text(text, 
                            reply_markup=Buttons.pr_main_buttons(replay_data).get_keyboard(1), 
                            parse_mode="MarkdownV2")
    
    @staticmethod
    def session_start_text(state_data: 'SessionStateData') -> str:
        ttr = state_data.session_settings.time_to_restart
        return f"```py\n" + insert_data(Text().get().cmds.session.sub_descr.ss_main_text,
                                        {"settings": '\n'.join([f"{param}: {getattr(state_data.session_settings, param)}" 
                                                                for param in ['is_autosession', "timezone"]] + \
                                                                [f"next restart: {ttr.hour}:{ttr.minute}"])}) + "\n```"

    @staticmethod
    async def session_back(msg: 'Message', state: 'FSMContext'):
        state_data = (await state.get_data())["data"]
        await msg.edit_text(text=Functions.session_start_text(state_data),
                            reply_markup=Buttons.session_start_session_buttons(state_data.session_settings.is_autosession) \
                            .get_keyboard(1),
                            parse_mode="MarkdownV2")
