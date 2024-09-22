from asyncio import sleep
from typing import TYPE_CHECKING
from datetime import datetime, timedelta

import pytz
from aiogram.types import BufferedInputFile

from lib.database.internal import InternalDB
from lib.data_parser.parse_data import get_session_stats
from lib.logger.logger import get_logger
from lib.settings.settings import Config
from lib.utils.calculate_exp import get_level
from lib.utils.string_parser import insert_data

from lib.api import API
from lib.locale.locale import Text
from lib.database.players import PlayersDB
from lib.image import SessionImageGen
from lib.data_classes.db_player import BadgesEnum, HookStatsTriggers, HookWatchFor, SessionStatesEnum

if TYPE_CHECKING:
    from aiogram import Bot

_config = Config().get()
_log = get_logger(__file__, 'TgWorkerPDBLogger', 'logs/tg_worker_pdb.log')


# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠀⢠⠀⠀⠀⠀⠀⠀⣠⠠⠀⠀⠂⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⡀⠀⠤⠀⠀⠀⠄⠀⠀⠀⠀⠀⡠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⡀⠐⠀⣆⠀⠀⠀⠀⠀⠐⠠⠀⠀⠑⢈⠓⠄⠠⢀⡀⢀⠀⠀⠀⠀⠀⢀⡀⡀⣀⠢⣄⡔⣁⣀⠢⠀⠑⠀⠀⢀⣞⠈⠀⣴⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⢐⡈⢻⠢⠀⠀⠀⠛⢉⠘⠒⠂⠠⠄⢀⠀⢀⠀⠀⠀⠈⠉⠉⠁⠀⠀⠀⠀⠀⢀⢔⣀⣀⠀⠀⠀⠀⠀⢀⠺⠈⢴⣕⠞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⢸⢆⠶⡆⢀⠀⡀⡀⢊⣉⠙⠒⠮⢀⣄⡀⠀⠈⠁⠂⠠⠤⠀⠀⠀⢠⠄⢒⠡⠏⠁⠀⡉⡉⡉⠒⠄⢀⠌⠚⢸⣇⡌⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠪⠿⡷⠘⠀⠡⠜⣰⣩⣦⣭⣠⣀⡀⠙⠙⠓⠠⠀⡄⠀⢀⣦⠀⡀⠈⢀⠀⣁⣀⣴⣦⣴⣬⣩⣄⡒⠁⣠⠙⢿⠁⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠢⠁⡀⣅⡀⣺⣿⣿⣿⣿⣿⣿⣽⣶⣶⣶⣶⣿⣶⡯⢍⡻⠿⣿⣿⣿⣿⣿⣿⣽⣿⣯⡛⡿⢿⡄⢠⡎⢀⡔⠪⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⠇⠿⢧⠉⠹⣿⡿⣻⣯⣟⣛⡭⣿⣿⣿⣿⣿⡷⠦⠴⣿⡿⡿⢿⣧⡝⣛⣯⣿⠿⢳⣗⠁⠘⡟⠃⠺⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢲⣾⠀⢸⠀⠀⠉⠳⢦⡼⠍⠽⢋⣏⠳⣼⣿⣿⠀⠀⠀⢸⣿⡷⢿⣿⣙⠫⠅⢁⣰⠯⠀⠀⢀⠇⠀⠿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⠀⠘⣆⠀⠀⠀⠀⠉⠤⠔⠋⠈⢀⣾⣿⠇⠀⠀⠀⠀⢻⣷⡈⠑⠓⠱⠲⠚⠃⠀⢀⣠⡞⠀⠀⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⡹⣳⢤⣤⣀⣀⣀⣄⣤⠼⢿⡛⠉⠉⠀⠀⠀⠀⠈⠙⠻⠶⢤⠤⣦⣴⣴⠶⠟⠑⡜⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⢱⣿⢿⡉⠋⠈⠀⠀⢀⣠⣿⠛⠀⠀⠀⠀⠀⠀⠀⠀⢷⣦⠀⠀⠀⠀⢀⠀⣌⢼⠼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣸⣹⡇⠀⠀⠀⠀⣾⣿⣇⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⣿⣷⣀⠀⠀⠀⢀⡏⣀⡎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠠⠁⢳⢗⣿⠈⣠⠰⣸⠟⠈⢿⣿⣦⣄⣀⠀⣄⣁⣠⣶⣾⣄⢙⣷⠂⢀⡀⣸⢬⠀⠀⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣦⠆⠀⠍⣿⣮⠜⠁⣴⣼⣾⣿⣿⣿⣿⣿⣿⣷⢿⣿⣿⣿⣿⣷⣿⣯⢳⢒⡿⣃⢀⢠⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⣿⣿⣾⡐⠆⢿⡇⡰⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⢘⠟⢆⣬⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⣾⣿⣿⣿⣿⣿⣿⡇⢇⢿⡧⣴⣿⣿⣿⠿⣿⢿⣿⣿⣿⣯⣿⣿⣿⣿⣿⣟⠛⣿⣿⣿⣸⢥⣼⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠈⢿⣗⢻⣽⣿⡏⠀⠀⠀⢀⣀⣤⣤⣤⣤⣀⡄⡀⠆⡄⢰⣾⣯⣭⢮⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠈⣿⡜⣽⣿⣧⡎⠔⣰⣽⣿⣿⣿⣿⣿⣿⣿⣦⣿⣶⣿⣿⣿⣵⠃⣟⡻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣤⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⠀⠠⠘⢀⢺⡷⣿⣿⣿⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣷⡪⣫⣿⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀
# ⠀⠀⠀⢀⣠⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠐⠀⡑⢊⠌⣻⣧⣽⣿⣿⣿⣿⣿⣿⣿⣿⣯⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⣵⣿⡯⣡⣿⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣤⡀⠀
# ⣠⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣔⠥⣉⠻⢹⡿⣿⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷
# ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣥⣚⡹⢟⣿⣧⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
# ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣷⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
# ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
#
# This guy make code more readable

_config = Config().get()


class PDBWorker:
    def __init__(self):
        self.db = PlayersDB()
        self.STOP_FLAG = False
        self.api = API()

    def stop_workers(self):
        """
        Stop the worker.

        This function sets the STOP_WORKER_FLAG to True, indicating that the worker should stop processing tasks.

        Parameters:
            None

        Returns:
            None
        """
        _log.debug('WORKERS: setting STOP_WORKER_FLAG to True')
        self.STOP_FLAG = True

    async def run_worker(self, bot: 'Bot', *args):
        """
        Asynchronously runs the worker in a loop.

        This function continuously checks the database and sleeps for 5 minutes
        before checking again. It stops running when the STOP_WORKER_FLAG is set
        to True.

        Parameters:
            None

        Returns:
            None
        """
        _log.info('WORKERS: PDB worker started')
        
        while not self.STOP_FLAG:
            await self.check_database(bot)
            await sleep(60 * 5)
            
        _log.info('WORKERS: PDB worker stopped')

    async def check_database(self, bot: 'Bot') -> None:
        """
        Check the database for any outdated data and update it if necessary.
        This function iterates over all the member IDs in the database and checks the data timestamp for each member.
        If the data is outdated, it updates the data for that member.
        It also checks the premium status for each member.

        Parameters:
            None

        Returns:
            None
        """
        member_ids = await self.db.get_all_members_ids()

        for member_id in member_ids:
            premium_members = await InternalDB().get_actual_premium_users()
            member = await self.db.get_member(member_id)
            
            if member_id in premium_members:
                premium = member.profile.premium
                premium_time = member.profile.premium_time
                if premium and premium_time is not None:
                    if premium_time < datetime.now(pytz.utc) + timedelta(seconds=3600):
                        await self.db.set_premium(member_id, datetime.now(pytz.utc) + timedelta(days=1))
                        _log.info(f'Set premium for {member_id}')
                elif not premium:
                    await self.db.set_premium(member_id, datetime.now(pytz.utc) + timedelta(days=1))
            
            if member.profile.last_activity < datetime.now(pytz.utc) - timedelta(seconds=_config.account.inactive_ttl):
                await self.db.delete_member(member_id)
                _log.warning(f'Deleted inactive member {member_id}')
            
            badges = member.profile.badges
            level = get_level(member.profile.level_exp)
            
            if level.level >= 5 and BadgesEnum.active_user.name not in badges:
                await self.db.set_badges(member_id, [BadgesEnum.active_user.name])
                
            if member.profile.premium and BadgesEnum.premium not in badges:
                await self.db.set_badges(member_id, [BadgesEnum.premium.name])
                
            used_slots = await self.db.get_all_used_slots(member=member)
            
            if len(used_slots) == 0:
                continue
                
            hook = member.hook_stats
            if hook.active:
                data = await self.api.get_stats(game_id=hook.last_stats.id, region=hook.target_region)
                session_diff = await get_session_stats(hook.last_stats, data, True)
                        
                if HookWatchFor(hook.watch_for) is HookWatchFor.DIFF:
                    stats_type = 'main_diff' if hook.stats_type == 'common' else 'rating_diff'
                    target_stats = getattr(session_diff, stats_type)
                elif HookWatchFor(hook.watch_for) is HookWatchFor.SESSION:
                    stats_type = 'main_session' if hook.stats_type == 'common' else 'rating_session'
                    target_stats = getattr(session_diff, stats_type)
                else:
                    stats_type = 'all' if hook.stats_type == 'common' else hook.stats_type
                    target_stats = getattr(data.data.statistics, stats_type)
                
                target_value = getattr(target_stats, hook.stats_name)

                if eval(f'{target_value} {HookStatsTriggers[hook.trigger].value} {hook.target_value}'):
                    _log.info(f'Hook triggered for {member_id}. Closing hook')
                    await self.db.disable_stats_hook(member_id)
                    image = SessionImageGen().generate(data, session_diff, member, 
                                                       member.current_slot, hide_nickname=False)
                    buffered_image = BufferedInputFile(image.read(), "hook.png")
                    lang = await self.db.get_lang(member_id)
                    lang = lang if lang != "auto" else hook.lang
                    await bot.send_photo(
                        hook.hook_target_chat_id,
                        buffered_image,
                        caption=insert_data(Text().get(lang).cmds.hook.info.hook_ended,
                                            {"user_id": member_id}),
                        parse_mode="MarkdownV2"
                    )
            
            for slot in used_slots:
                game_account = await self.db.get_game_account(slot, member=member)
                session_state = await self.db.validate_session(member=member, slot=slot)
                
                if session_state is not SessionStatesEnum.RESTART_NEEDED:
                    continue
                
                new_last_stats = await self.api.get_stats(game_id=game_account.game_id, region=game_account.region)
                game_account.session_settings.time_to_restart += timedelta(days=1)
                _log.info(f'Session updated for {member_id} in slot {slot.name}')
                await self.db.update_session(slot, member_id, game_account.session_settings, new_last_stats)
                await sleep(0.1)
