from typing import TYPE_CHECKING

from aiogram.types import BufferedInputFile

from ex_func import StatsFunc
from lib.image import CommonImageGen
from lib.exceptions.common import HookExceptions
from lib.data_parser.parse_replay import ParseReplayData
from lib.data_classes.state_data import ReplayParserStateData
from lib.data_classes.image import CommonImageGenExtraSettings

from ..buttons import Buttons
from ..functions import Functions, ReplayParseSupport

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import CallbackQuery
    from aiogram.fsm.context import FSMContext
    
    from lib.database.players import PlayersDB


class ParseReplayHandlers:
    pdb: 'PlayersDB'

    @HookExceptions().hook()
    async def parse_replay_main_back_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        await state.set_state()
        await data.message.delete()
        await data.answer("✅")

    @HookExceptions().hook(del_message_on_error=True)
    async def pr_region_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        region = data.data.split(":")[1]
        teams = [[], []]
        parsed_replay_data = await ParseReplayData().parse((await state.get_data())["data"], region)
        for player in parsed_replay_data.players:
            teams[player.info.team - 1].append(player)

        await state.update_data({"data": ReplayParserStateData(region=region, 
                                                               replay_data=parsed_replay_data,
                                                               team1=teams[0],
                                                               team2=teams[1])})

        await Functions.parse_replay_main_message(data.message, data.from_user, parsed_replay_data, region)
    
    @HookExceptions().hook(del_message_on_error=True)
    async def pr_team_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        team_number = int(data.data.split(":")[1])
        state_data: 'ReplayParserStateData' = (await state.get_data())["data"]
        team = state_data.team1 if team_number == 1 else state_data.team2
        await data.message.edit_reply_markup(reply_markup=Buttons.pr_team_buttons(team, team_number).get_keyboard(1))
    
    @HookExceptions().hook(del_message_on_error=True)
    async def pr_player_handle(self, data: 'CallbackQuery', state: 'FSMContext', bot: 'Bot', **_):
        team_number, ind = [int(i) for i in data.data.split(":")[1:]]
        state_data: 'ReplayParserStateData' = (await state.get_data())["data"]
        player = state_data.replay_data.players[ind]

        for player_result in state_data.replay_data.player_results:
            if player_result.info.account_id == player.account_id:
                break

        text = await ReplayParseSupport.get_text_by_player(player_result, state_data.region)

        if (team_number, ind) in state_data.cache:
            file = BufferedInputFile(state_data.cache.get((team_number, ind)), 
                                     filename=f"{player.info.nickname}.jpg")
            await bot.send_photo(data.message.chat.id, file, caption=text, parse_mode="MarkdownV2")
            await data.answer("✅")
            return

        team = state_data.team1 if team_number == 1 else state_data.team2
        player = team[ind]
        player_stats = await StatsFunc.get_stats(player.account_id, player.info.nickname, state_data.region)

        if isinstance(player_stats, str):
            await data.answer(player_stats)
            return

        member = await self.pdb.get_member(data.from_user.id)
        img = CommonImageGen().generate(player_stats, member, member.current_slot, extra=CommonImageGenExtraSettings())
        img_bytes = img.read()
        
        file = BufferedInputFile(img_bytes, filename=f"{player.info.nickname}.png")
        state_data.cache.set((team_number, ind), img_bytes)

        await data.answer("✅")
        await bot.send_photo(data.message.chat.id, file, caption=text, parse_mode="MarkdownV2")

    @HookExceptions().hook(del_message_on_error=True)
    async def pr_back_handle(self, data: 'CallbackQuery', state: 'FSMContext', **_):
        state_data: 'ReplayParserStateData' = (await state.get_data())["data"]
        await data.message.edit_reply_markup(reply_markup=Buttons.pr_main_buttons(state_data.replay_data).get_keyboard(1))
