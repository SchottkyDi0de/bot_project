from asyncio import sleep
from datetime import datetime, timedelta

from discord import Bot
import pytz

from lib.api.async_wotb_api import API
from lib.data_classes.db_player import BadgesEnum, HookStatsTriggers, HookWatchFor, SessionStatesEnum
from lib.database.internal import InternalDB
from lib.database.players import PlayersDB
from lib.locale.locale import Text
from lib.logger.logger import get_logger
from lib.settings.settings import Config
from lib.utils.calculate_exp import get_level
from lib.embeds.info import InfoMSG
from lib.data_parser.parse_data import get_session_stats
from lib.utils.string_parser import insert_data

_log = get_logger(__file__, 'WorkerPDBLogger', 'logs/worker_pdb.log')
_config = Config().get()

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

class PDBWorker:
    def __init__(self):
        self.db = PlayersDB()
        self.STOP_FLAG = False
        self.api = API()
        self.bot = None

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

    async def run_worker(self, bot: Bot, *args):
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
        self.bot = bot
        _log.info('WORKERS: PDB worker started')
        
        while not self.STOP_FLAG:
            await self.check_database()
            await sleep(200)
            
        _log.info('WORKERS: PDB worker stopped')

    async def check_database(self) -> None:
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
            
            for slot in used_slots:
                game_account = await self.db.get_game_account(slot, member=member)
                session_state = await self.db.validate_session(member=member, slot=slot)
                
                if session_state is SessionStatesEnum.NORMAL:
                    hook = game_account.hook_stats
                    if hook.active:
                        data = await self.api.get_stats(game_id=game_account.game_id, region=game_account.region)
                        session_diff = await get_session_stats(game_account.last_stats, data, True)
                        
                        if HookWatchFor(hook.watch_for) is HookWatchFor.DIFF:
                            stats_type = 'main_diff' if hook.stats_type == 'common' else 'rating_diff'
                            target_stats = getattr(getattr(session_diff, stats_type), hook.stats_name)
                        elif HookWatchFor(hook.watch_for) is HookWatchFor.SESSION:
                            stats_type = 'main_session' if hook.stats_type == 'common' else 'rating_session'
                            target_stats = getattr(getattr(session_diff, stats_type), hook.stats_name)
                        else:
                            stats_type = 'all' if hook.stats_type == 'common' else hook.stats_type
                            target_stats = getattr(getattr(data.data.statistics, stats_type), hook.stats_name)
                        
                        if eval(f'{target_stats} {HookStatsTriggers[hook.trigger].value} {hook.target_value}'):
                            _log.info(f'Hook triggered for {member_id} in slot {slot.name}. Closing hook')
                            await self.db.disable_stats_hook(member_id, slot)
                            guild = await self.bot.fetch_guild(hook.hook_target_guild_id)
                            channel = await guild.fetch_channel(hook.hook_target_channel_id)
                            await channel.send(
                                f'<@{hook.hook_target_member_id}>',
                                embed=InfoMSG().custom(
                                    locale=Text().get(hook.lang),
                                    text=insert_data(
                                        Text().get(hook.lang).cmds.hook_stats.info.triggered,
                                        {
                                            'watch_for': hook.watch_for,
                                            'stats_name': hook.stats_name,
                                            'target_stats': round(target_stats, 4),
                                            'trigger': HookStatsTriggers[hook.trigger].value,
                                            'value': round(hook.target_value, 4)
                                        }
                                    
                                    )
                                )
                            )
                                    
                        if hook.end_time < datetime.now(pytz.utc):
                            _log.info(f'Closing hook for {member_id} in slot {slot.name} - hook expired')
                            await self.db.disable_stats_hook(member_id, slot)
                
                if session_state is not SessionStatesEnum.RESTART_NEEDED:
                    continue
                
                new_last_stats = await self.api.get_stats(game_id=game_account.game_id, region=game_account.region)
                game_account.session_settings.time_to_restart += timedelta(days=1)
                _log.info(f'Session updated for {member_id} in slot {slot.name}')
                await self.db.update_session(slot, member_id, game_account.session_settings, new_last_stats)
                await sleep(0.1)
