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
        Checks the database for inactive members, updates their premium status, and performs various other tasks.
        
        This function retrieves all member IDs from the database using `self.db.get_all_members_ids()`. It then iterates over each member ID and performs the following tasks:
        
        1. Retrieves the premium members from the internal database using `InternalDB().get_actual_premium_users()`.
        2. Retrieves the member details from the database using `self.db.get_member(member_id)`.
        3. If the member ID is in the list of premium members, it checks if the member is already marked as premium and if the premium time has expired. If it has, it updates the premium time to one day from the current time using `self.db.set_premium(member_id, datetime.now(pytz.utc) + timedelta(days=1))`.
        4. If the member is not marked as premium, it sets the premium time to one day from the current time.
        5. Checks if the member's last activity is older than the inactive TTL specified in `_config.account.inactive_ttl`. If it is, it deletes the member from the database using `self.db.delete_member(member_id)`.
        6. Retrieves the member's badges and level using `member.profile.badges` and `get_level(member.profile.level_exp())`.
        7. If the member's level is 5 or higher and the `active_user` badge is not present, it adds the `active_user` badge to the member's badges using `self.db.set_badges(member_id, [BadgesEnum.active_user.name])`.
        8. If the member is marked as premium and the `premium` badge is not present, it adds the `premium` badge to the member's badges.
        9. Retrieves the used slots for the member using `self.db.get_all_used_slots(member=member)`.
        10. If there are no used slots, it continues to the next iteration.
        11. For each used slot, it retrieves the game account using `self.db.get_game_account(slot, member=member)`.
        12. It validates the session using `self.db.validate_session(member=member, slot=slot)`.
        13. If the session state is `NORMAL`, it checks if the stats hook is active for the game account.
        14. If the hook is active, it retrieves the game statistics using `self.api.get_stats(game_id=game_account.game_id, region=game_account.region)`.
        15. It calculates the session difference using `get_session_stats(game_account.last_stats, data, True)`.
        16. It checks the type of hook watch for and retrieves the target stats accordingly.
        17. It evaluates the target stats against the hook trigger and target value.
        18. If the evaluation is true, it triggers the hook by disabling the stats hook, sending a message to a specific channel, and updating the hook settings in the database.
        19. If the hook end time has passed, it disables the stats hook.
        20. If the session state is `RESTART_NEEDED`, it updates the session settings and retrieves new statistics using `self.api.get_stats(game_account.game_id, game_account.region)`.
        21. It updates the session in the database using `self.db.update_session(slot, member_id, game_account.session_settings, new_last_stats)`.
        
        This function does not return any value.
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
                continue
            
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
                
                hook = game_account.hook_stats
                if hook.active:
                    try:
                        data = await self.api.get_stats(game_id=hook.target_game_id, region=hook.target_game_region)
                    except Exception:
                        _log.warning(f'Failed to get stats for {member_id} in slot {slot.name}')
                        await self.db.disable_stats_hook(member_id, slot)
                        continue
                    
                    session_diff = await get_session_stats(hook.last_stats, data, True)
                    
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
                        guild = await self.bot.fetch_guild(hook.target_guild_id)
                        channel = await guild.fetch_channel(hook.target_channel_id)
                        await channel.send(
                            f'<@{hook.target_member_id}>',
                            embed=InfoMSG().custom(
                                locale=Text().get(hook.lang),
                                text=insert_data(
                                    Text().get(hook.lang).cmds.hook_stats.info.triggered,
                                    {
                                        'target_player': hook.last_stats.nickname,
                                        'watch_for': hook.watch_for,
                                        'stats_name': hook.stats_name,
                                        'target_stats': round(target_stats, 4),
                                        'trigger': HookStatsTriggers[hook.trigger].value,
                                        'value': round(hook.target_value, 4)
                                    }
                                )
                            )
                        )
                        await self.db.disable_stats_hook(member_id, slot)
                                
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
