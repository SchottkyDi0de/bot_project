from datetime import datetime

from discord.ext import commands
from discord.file import File

from lib.image.common import ImageGen
from lib.database.players import PlayersDB
from lib.database.servers import ServersDB
from lib.locale.locale import Text
from lib.exceptions.database import MemberNotFound

from lib.data_classes.api_data import PlayerGlobalData, Player
from lib.data_classes.player_achievements import Achievements
from lib.data_classes.player_stats import Statistics, All as all_player, Rating
from lib.data_classes.tanks_stats import TankStats, All as all_tank
from lib.data_classes.player_clan_stats import Clan
from lib.data_classes.db_player import ImageSettings

class _PreviewData:
    achievements = Achievements.model_validate({"mainGun": 100, "medalRadleyWalters": 100, 
                                                "medalKolobanov": 100, "markOfMastery": 100, "warrior": 100})
    clan = Clan.model_validate({
        "members_count": 50,
        "name": "BlitzHub",
        "created_at": 946684801,
        "tag": "B_HUB",
        "clan_id": 1,
        "emblem_set_id": 1
    })
    all_stats_player = all_player.model_validate({
        "spotted": 1000,
        "max_frags_tank_id": 0,
        "hits": 1000,
        "max_frags": 7,
        "frags": 1000,
        "max_xp": 1000,
        "wins": 1000,
        "losses": 1000,
        "capture_points": 1000,
        "battles": 2000,
        "damage_dealt": 1000,
        "damage_received": 1000,
        "shots": 1000,
        "frags8p": 1000,
        "xp": 1000,
        "win_and_survived": 1000,
        "survived_battles": 1000,
        "dropped_capture_points": 1000,
        "max_xp": 1000,

        "avg_xp": 1000.0,
        "avg_damage": 1000.0,
        "accuracy": 90.0,
        "winrate": 50.0,
        "avg_spotted": 1000.0,
        "frags_per_battle": 5.0,
        "not_survived_battles": 1000,
        "survival_ratio": 50.0,
        "damage_ratio": 1000.0,
        "destruction_ratio": 1000.0
    })
    rating_stats = Rating.model_validate({
        "spotted": 1000,
        "calibration_battles_left": 0,
        "hits": 1000,
        "frags": 1000,
        "recalibration_start_time": 946684801,
        "mm_rating": 5000,
        "wins": 1000,
        "losses": 1000,
        "is_recalibration": False,
        "capture_points": 1000,
        "battles": 2000,
        "current_season": 1,
        "damage_dealt": 1000,
        "damage_received": 1000,
        "shots": 1000,
        "frags8p": 1000,
        "xp": 1000,
        "win_and_survived": 1000,
        "survived_battles": 1000,
        "dropped_capture_points": 1000,
        "max_xp": 1000,

        "winrate": 50.0,
        "rating": 5000
    })
    all_tank_stats = all_tank.model_validate({
        "spotted": 1000,
        "max_frags_tank_id": 1,
        "hits": 1000,
        "max_frags": 7,
        "frags": 1000,
        "wins": 1000,
        "losses": 1000,
        "capture_points": 1000,
        "battles": 2000,
        "damage_dealt": 1000,
        "damage_received": 1000,
        "shots": 1000,
        "frags8p": 1000,
        "xp": 1000,
        "win_and_survived": 1000,
        "survived_battles": 1000,
        "dropped_capture_points": 1000,
        "max_xp": 1000
    })
    statistics = Statistics.model_validate({
        "all": all_stats_player,
        "rating": rating_stats
    })
    tank_stats = TankStats.model_validate({
        "all": all_tank_stats,
        "last_battle_time": 946684801,
        "account_id": 1,
        "max_xp": 1000,
        "in_garage_updated": 946684801,
        "max_frags": 7,
        "frags": 1000,
        "mark_of_mastery": 100,
        "battle_life_time": 946684801,
        "in_garage": True,
        "tank_id": 1
    })
    player = Player.model_validate({
        "achievements": achievements,
        "clan_stats": clan,
        "tank_stats": {"1": tank_stats},
        "statistics": statistics,
        "name_and_tag": "",
        "clan_tag": "B_HUB"
    })
    player_global_data = lambda nickname, region: PlayerGlobalData.model_validate({
        "id": 1,
        "data": _PreviewData.player,
        "region": region,
        "lower_nickname": nickname.lower(),
        "timestamp": datetime.utcnow(),
        "nickname": nickname
        })


class StatsPriview:
    def __init__(self) -> None:
        self.pdb = PlayersDB()
        self.sdb = ServersDB()
    
    async def preview(self, ctx: commands.Context, image_settings: ImageSettings) -> None:
        server_settings = self.sdb.get_server_settings(ctx)
        try:
            player_data = self.pdb.get_member(ctx.author.id)
            nickname, region, lang = player_data.nickname, player_data.region, player_data.lang
        except MemberNotFound:
            nickname, region, lang = 'Nickname', 'ru', 'eu'
        player_global_data = _PreviewData.player_global_data(nickname, region)
        image = ImageGen().generate(ctx, player_global_data, image_settings, server_settings)
        await ctx.respond(Text().get(lang).cmds.image_settings.info.preview, file=File(image, 'stats.png'), ephemeral=True)
