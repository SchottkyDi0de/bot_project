import pytz
from typing import TYPE_CHECKING
from datetime import datetime, timedelta

from aiogram import  F
from aiogram.filters import Command

from lib.logger.logger import get_logger
from lib.utils.time_converter import TimeConverter
from lib.utils.string_parser import insert_data
from lib.utils.validators import RawRegex

from extensions.setup import ExtensionsSetup
from ex_func import SessionFunc, SessionImageGenFunc
from lib import (API, Buttons, CooldownStorage, PlayersDB, HookExceptions,
                 AutoSessionStates, Text, Activities, analytics, check)

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message
    from aiogram.fsm.context import FSMContext


_log = get_logger(__file__, 'TgSessionLogger', 'logs/tg_session.log')


class Session(ExtensionsSetup):
    __funcs_filters__ = [
        ("start_session", (Command("start_session"),)),
        ("session_state", (Command("session_state"),)),
        ("get_session", (Command("get_session"),)),
        ("session", (Command("session"),)),
        ("start_autosession", (Command("start_autosession"),)),
        ("start_autossesion_timezone", (F.text.in_([f"{i}" for i in range(13)]), AutoSessionStates.set_timezone)),
        ("invalid_timezone", (AutoSessionStates.set_timezone,),),
        ("start_autossesion_restart", (F.text.regexp(RawRegex.time), AutoSessionStates.set_restart_time),),
        ("invalid_restart_time", (AutoSessionStates.set_restart_time,),),
    ]

    def init(self) -> None:
        self.api = API()
        self.pdb = PlayersDB()

    @HookExceptions().hook(_log)
    @Activities.typing
    @check()
    @analytics()
    async def start_session(self, msg: 'Message', **_):
        member = await self.pdb.get_member(msg.from_user.id)
        member_current_account = member.current_account
        last_stats = await self.api.get_stats(
            game_id=member_current_account.game_id,
            region=member_current_account.region,
            requested_by=member
        )
        
        await SessionFunc.start_session(member.current_slot, member, last_stats)

        await msg.reply(Text().get().cmds.start_session.info.started)
    
    @HookExceptions().hook(_log)
    @Activities.typing
    @check()
    @CooldownStorage.cooldown(10)
    @analytics()
    async def session_state(self, msg: 'Message', bot: 'Bot', **_):
        member = await self.pdb.get_member(msg.from_user.id)
        if await self.pdb.check_member_last_stats(member.current_slot, msg.from_user.id, member):
            text = await SessionFunc.session_state(member.current_slot, member)
            await msg.reply(text, parse_mode='MarkdownV2')
            await bot.send_message(msg.chat.id, Text().get().cmds.session_state.items.started_part2)
        else:
            await msg.reply(Text().get().cmds.session_state.items.not_started)
    
    @HookExceptions().hook(_log)
    @Activities.upload_photo
    @check()
    @CooldownStorage.cooldown(10, "update_sesion")
    @analytics()
    async def get_session(self, msg: 'Message', **_):
        member = await self.pdb.get_member(msg.from_user.id)
        await msg.reply_photo(await SessionImageGenFunc.generate_image(member.current_slot, msg.from_user.id),
                              caption=datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S"),
                              reply_markup=Buttons.get_session_buttons(msg.from_user.id).get_keyboard())
    
    @HookExceptions().hook(_log)
    @Activities.typing
    @check()
    @analytics()
    async def start_autosession(self, msg: 'Message', state: 'FSMContext', **_):
        await state.set_state(AutoSessionStates.set_timezone)
        await msg.reply(Text().get().cmds.start_autosession.sub_descr.get_timezone, 
                        reply_markup=Buttons.start_autossession_timezone_buttons().get_keyboard())
    
    @HookExceptions().hook(_log)
    @Activities.typing
    async def start_autossesion_timezone(self, msg: 'Message', state: 'FSMContext', **_):
        await state.set_state(AutoSessionStates.set_restart_time)
        await state.update_data(data={"data": {"timezone": msg.text}})
        await msg.reply(Text().get().cmds.start_autosession.sub_descr.get_restart_time, 
                        reply_markup=Buttons.start_autossesion_restart_buttons().get_keyboard())
    
    @HookExceptions().hook(_log)
    @Activities.typing
    async def start_autossesion_restart(self, msg: 'Message', state: 'FSMContext', **_):
        data = (await state.get_data())["data"]
        timezone = int(data['timezone'])
        restart_time = msg.text

        del data['timezone']
        await state.update_data(data={"data": None})

        now_time = datetime.now(tz=pytz.utc).replace(hour=0, minute=0, second=0)
        member = await self.pdb.get_member(msg.from_user.id)
        account = member.current_account
            
        session_settings = await self.pdb.get_session_settings(member.current_slot, msg.from_user.id, member)
        session_settings.last_get = datetime.now(tz=pytz.utc)
        session_settings.is_autosession = True
            
        if timezone is not None:
            session_settings.timezone = timezone
            
        session_settings.time_to_restart = (
            now_time + timedelta(
                seconds=TimeConverter.secs_from_str_time(restart_time)
                )
        )
                
        last_stats = await self.api.get_stats(
            region=account.region, 
            game_id=account.game_id,
            requested_by=member
        )
        await self.pdb.start_session(member.current_slot, msg.from_user.id, last_stats, session_settings)
        await msg.reply(Text().get().cmds.start_autosession.info.started, 
                        reply_markup=Buttons.remove_buttons("reply"))
        await state.set_state()
    
    @HookExceptions().hook(_log)
    @Activities.typing
    @check()
    async def session(self, msg: 'Message', **_):
        member = await self.pdb.get_member(msg.from_user.id)
        last_stats = await self.pdb.check_member_last_stats(member.current_slot, msg.from_user.id, member)
        if last_stats:
            s_state = await SessionFunc.session_state(member.current_slot, member)
        else:
            s_state = f"```py\n{Text().get().cmds.session_state.items.not_started}```"
        
        await msg.reply(insert_data(Text().get().cmds.session.descr,
                                    {"state": s_state}), 
                        parse_mode='MarkdownV2',
                        reply_markup=Buttons.session_main_buttons(last_stats).get_keyboard(1))

    
    @HookExceptions().hook(_log)
    @Activities.typing
    async def invalid_timezone(self, msg: 'Message', **_):
        await msg.reply(Text().get().cmds.start_autosession.errors.uncorrect_tz)
    
    @HookExceptions().hook(_log)
    @Activities.typing
    async def invalid_restart_time(self, msg: 'Message', **_):
        await msg.reply(insert_data(Text().get().cmds.start_autosession.errors.uncorrect_r_time, 
                                    {'time': msg.text}))
