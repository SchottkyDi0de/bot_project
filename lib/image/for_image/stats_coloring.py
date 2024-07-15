from lib.data_classes.db_player import ImageSettings
from lib.image.for_image.colors import StatsColors as Colors

def colorize(stats_type: str, stats_value: str | float | int, default_color: tuple[int], rating: bool = False) -> tuple | None:
        """
        Returns a color based on the given stats_type and stats_value.

        Parameters:
            stats_type (str): The type of statistics.
            stats_value (int or float): The value of the statistics.
            rating (bool, optional): Whether to use a different range for the 'battles' stats_type. Defaults to False.

        Returns:
            str: The color corresponding to the stats_value and stats_type.

        Raises:
            None

        Examples:
            >>> colorize('winrate', 55)
            (205, 106, 29)
            >>> colorize('avg_damage', 1500)
            (30, 255, 38)
            >>> colorize('battles', 10000, rating=True)
            (116, 30, 169)
        """
        if not isinstance(stats_type, str):
            return default_color
        
        stats_type = stats_type.replace('r_', '')
        stats_type = stats_type.replace('d_', '')
        stats_type = stats_type.replace('s_', '')
        
        if not isinstance(stats_value, (int, float, str)):
            return default_color

        val = stats_value
        
        if isinstance(val, str):
            val = val.replace('-', '')
            val = val.replace('+', '')
            val = val.replace('%', '')
            try:
                val = float(val)
            except ValueError:
                val = -1

        if val == -1:
            return default_color
        
        if stats_type == 'winrate':
            if val < 44:
                return Colors.grey
            elif val < 60:
                return Colors.green
            elif val < 70:
                return Colors.cyan
            elif val >= 70:
                return Colors.purple

        elif stats_type == 'avg_damage':
            if val < 1200:
                return Colors.grey
            elif val < 1700:
                return Colors.green
            elif val < 2500:
                return Colors.cyan
            else:
                return Colors.purple

        elif stats_type == 'battles':
            if val < 2000:
                return Colors.grey
            elif val < 10000:
                return Colors.green
            elif val < 30000:
                return Colors.cyan
            else:
                return Colors.purple

        elif stats_type == 'battles' and rating:
            if val < 1000:
                return Colors.grey
            elif val < 3000:
                return Colors.green
            elif val < 6000:
                return Colors.cyan
            else:
                return Colors.purple

        elif stats_type == 'frags_per_battle':
            if val < 1:
                return Colors.grey
            elif val < 1.2:
                return Colors.green
            elif val < 1.3:
                return Colors.cyan
            else:
                return Colors.purple

        elif stats_type == 'damage_ratio':
            if val < 1:
                return Colors.grey
            elif val < 1.3:
                return Colors.green
            elif val < 2:
                return Colors.cyan
            else:
                return Colors.purple

        elif stats_type == 'destruction_ratio':
            if val < 1:
                return Colors.grey
            elif val < 1.4:
                return Colors.green
            elif val < 2.4:
                return Colors.cyan
            else:
                return Colors.purple

        elif stats_type == 'avg_spotted':
            if val < 1:
                return Colors.grey
            elif val < 1.2:
                return Colors.green
            elif val < 1.5:
                return Colors.cyan
            else:
                return Colors.purple

        elif stats_type == 'accuracy':
            if val < 70:
                return Colors.grey
            elif val < 75:
                return Colors.green
            elif val < 85:
                return Colors.cyan
            else:
                return Colors.purple
            
        elif stats_type == 'leaderboard_position':
            if val <= 500:
                return Colors.green
            elif val <= 100:
                return Colors.cyan
            elif val <= 20:
                return Colors.purple
            elif val == 1:
                return Colors.gold
            else:
                return Colors.grey
        else:
            return default_color
