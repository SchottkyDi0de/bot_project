import struct

class TeamNumber:
    One = 1
    Two = 2

class BattleResults:
    def __init__(self, mode_map_id, timestamp_secs, winner_team_number, author, room_type, free_xp, players, player_results):
        self.mode_map_id = mode_map_id
        self.timestamp_secs = timestamp_secs
        self.winner_team_number = winner_team_number
        self.author = author
        self.room_type = room_type
        self.free_xp = free_xp
        self.players = players
        self.player_results = player_results

class Player:
    def __init__(self, account_id, info):
        self.account_id = account_id
        self.info = info

class PlayerInfo:
    def __init__(self, nickname, platoon_id, team, clan_tag, avatar, rank):
        self.nickname = nickname
        self.platoon_id = platoon_id
        self.team = team
        self.clan_tag = clan_tag
        self.avatar = avatar
        self.rank = rank

class PlayerResults:
    def __init__(self, result_id, info):
        self.result_id = result_id
        self.info = info

class PlayerResultsInfo:
    def __init__(self, credits_earned, base_xp, n_shots, n_hits_dealt, n_penetrations_dealt, damage_dealt, damage_assisted_1, damage_assisted_2, n_hits_received, n_non_penetrating_hits_received, n_penetrations_received, n_enemies_damaged, n_enemies_destroyed, victory_points_earned, victory_points_seized, account_id, tank_id, mm_rating, damage_blocked):
        self.credits_earned = credits_earned
        self.base_xp = base_xp
        self.n_shots = n_shots
        self.n_hits_dealt = n_hits_dealt
        self.n_penetrations_dealt = n_penetrations_dealt
        self.damage_dealt = damage_dealt
        self.damage_assisted_1 = damage_assisted_1
        self.damage_assisted_2 = damage_assisted_2
        self.n_hits_received = n_hits_received
        self.n_non_penetrating_hits_received = n_non_penetrating_hits_received
        self.n_penetrations_received = n_penetrations_received
        self.n_enemies_damaged = n_enemies_damaged
        self.n_enemies_destroyed = n_enemies_destroyed
        self.victory_points_earned = victory_points_earned
        self.victory_points_seized = victory_points_seized
        self.account_id = account_id
        self.tank_id = tank_id
        self.mm_rating = mm_rating
        self.damage_blocked = damage_blocked

class Author:
    def __init__(self, hitpoints_left, total_credits, total_xp, n_shots, n_hits, n_splashes, n_penetrations, damage_dealt, account_id, team_number):
        self.hitpoints_left = hitpoints_left
        self.total_credits = total_credits
        self.total_xp = total_xp
        self.n_shots = n_shots
        self.n_hits = n_hits
        self.n_splashes = n_splashes
        self.n_penetrations = n_penetrations
        self.damage_dealt = damage_dealt
        self.account_id = account_id
        self.team_number = team_number

class Avatar:
    def __init__(self, info):
        self.info = info

class AvatarInfo:
    def __init__(self, gfx_url, gfx2_url, kind):
        self.gfx_url = gfx_url
        self.gfx2_url = gfx2_url
        self.kind = kind

def parse_player(player):
    player_info = player.split(',')
    player_id = player_info[0].strip()
    player_name = player_info[1].strip()
    return player_id, player_name

def parse_player_results(player_results):
    results = []
    for result in player_results:
        result_info = result.split(',')
        result_id = result_info[0].strip()
        result_score = result_info[1].strip()
        results.append((result_id, int(result_score)))
    return results

def parse_battle_results(filename):
    with open(filename, "rb") as f:
        buffer = f.read()
        mode_map_id, timestamp_secs, winner_team_number, author, room_type, free_xp, = struct.unpack("<IqiiI", buffer[:28])
        
        players = []
        offset = 28
        n_players = struct.unpack("<I", buffer[offset:offset+4])[0]
        offset += 4
        for _ in range(n_players):
            account_id, info = parse_player(buffer, offset)
            players.append(Player(account_id, info))
            offset += 100
        
        player_results = []
        offset += 4
        n_results = struct.unpack("<I", buffer[offset:offset+4])[0]
        offset += 4
        for _ in range(n_results):
            result_id, info = parse_player_results(buffer, offset)
            player_results.append(PlayerResults(result_id, info))
            offset += 156
        
        return BattleResults(mode_map_id, timestamp_secs, winner_team_number, author, room_type, free_xp, players, player_results)
    
parse_battle_results('battle_results.dat')
