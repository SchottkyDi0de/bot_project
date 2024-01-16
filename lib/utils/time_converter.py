from datetime import datetime, timedelta


class TimeConverter:
    @staticmethod
    def formatted_from_secs(
            seconds: int, 
            format: str = '%H:%M:%S') -> str:
        """
        Converts a given number of seconds to a formatted time string.

        Args:
            seconds (int): The number of seconds to convert.
            format (str, optional): The format of the time string. Defaults to '%H:%M:%S'.

        Returns:
            str: The formatted time string.

        Example:
            >>> from_seconds(3661, '%H hours, %M minutes, and %S seconds')
            '1 hour, 1 minute, and 1 second'
        """
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        time_str = format

        for i in format.split('%'):
            if i[0:1] == 'H':
                time_str = time_str.replace('%H', str(h), 1)

            if i[0:1] == 'M':
                time_str = time_str.replace('%M', str(m), 1)

            if i[0:1] == 'S':
                time_str = time_str.replace('%S', str(s), 1)

        return time_str
    
    def secs_from_time(time: datetime) -> int:
        return int(timedelta(hours=time.hour, minutes=time.minute).total_seconds())
    
    def secs_from_str_time(time: str) -> int:
        time_data = datetime.strptime(time, '%H:%M')
        return int(timedelta(hours=time_data.hour, minutes=time_data.minute).total_seconds())