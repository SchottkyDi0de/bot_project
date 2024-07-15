from PIL import Image


class StatsIcons:
    accuracy: Image.Image = Image.open('res/icons/for_stats/accuracy.png')
    avg_damage: Image.Image = Image.open('res/icons/for_stats/avg_damage.png')
    avg_spotted: Image.Image = Image.open('res/icons/for_stats/avg_spotted.png')
    battles: Image.Image = Image.open('res/icons/for_stats/battles.png')
    damage_dealt: Image.Image = Image.open('res/icons/for_stats/damage_dealt.png')
    damage_ratio: Image.Image = Image.open('res/icons/for_stats/damage_ratio.png')
    destruction_ratio: Image.Image = Image.open('res/icons/for_stats/destruction_ratio.png')
    frags: Image.Image = Image.open('res/icons/for_stats/frags.png')
    frags_per_battle: Image.Image = Image.open('res/icons/for_stats/kills_per_battle.png')
    max_frags: Image.Image = Image.open('res/icons/for_stats/max_frags.png')
    shots: Image.Image = Image.open('res/icons/for_stats/shots.png')
    survived: Image.Image = Image.open('res/icons/for_stats/survived.png')
    winrate: Image.Image = Image.open('res/icons/for_stats/winrate.png')
    xp: Image.Image = Image.open('res/icons/for_stats/xp.png')
    max_xp: Image.Image = Image.open('res/icons/for_stats/max_xp.png')
    losses: Image.Image = Image.open('res/icons/for_stats/loose.png')
    capture_points: Image.Image = Image.open('res/icons/for_stats/capture_points.png')

    winrate_r = winrate
    battles_r = battles
    survived_battles = survived
    hits = damage_dealt
    wins = winrate
    damage_received = damage_dealt.rotate(180).copy()
    dropped_capture_points = capture_points
    survival_ratio = survived
    leaderboard_position = capture_points
    
class LeaguesIcons:
    gold = Image.open('res/icons/leagues/gold.png')
    platinum = Image.open('res/icons/leagues/platinum.png')
    brilliant = Image.open('res/icons/leagues/brilliant.png')
    calibration = Image.open('res/icons/leagues/calibr.png')
    empty = Image.open('res/icons/leagues/no-rating.png')