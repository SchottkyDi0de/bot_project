class ValueNormalizer():
    @staticmethod
    def winrate(val, enable_null=False):
        """
        Normalizes a winrate value.

        Args:
            val (float): The winrate value to normalize.

        Returns:
            str: The normalized winrate value as a string.
                  If val is 0, returns '—'.
                  Otherwise, returns the winrate value formatted as '{:.2f} %'.
        """
        if round(val, 2) == 0:
            if not enable_null:
                return '—'
            else:
                return '0'

        return '{:.2f}'.format(abs(val)) + '%'

    @staticmethod
    def ratio(val, enable_null=False):
        """
        Normalizes a ratio value.

        Args:
            val (float): The ratio value to normalize.

        Returns:
            str: The normalized ratio value as a string.
                  If val is 0, returns '—'.
                  Otherwise, returns the ratio value formatted as '{:.2f}'.
        """
        return ValueNormalizer.winrate(val, enable_null).replace('%', '')
    
    @staticmethod
    def other(val, enable_null=False, str_bypass=False):
        """
        Normalizes a value based on certain conditions.

        Args:
            val (float or int): The value to normalize.
            enable_null (bool): If True, returns '0' for zero values. Defaults to False.
            str_bypass (bool): If True, returns the value as a string if it's a string. Defaults to False.

        Returns:
            str:
            The normalized value as a string.
            If val is 0 or equal to 0, returns '—' if enable_null is False, else '0'.
            If val is a string, returns '—'.
            If val is between 100,000 and 1,000,000, returns the value divided by 1,000
            rounded to 2 decimal places and appended with 'K'.
            If val is greater than or equal to 1,000,000, returns the value divided by 1,000,000
            rounded to 2 decimal places and appended with 'M'.
            Otherwise, returns the value as a string.
        """
        # Convert value to string if str_bypass is True and it's a string
        if str_bypass and isinstance(val, str):
            return val

        # Check if value is 0 or equal to 0, return special value if enable_null is False
        if round(val) == 0:
            if not enable_null:
                return '—'
            else:
                return '0'

        # Check if value is a string, return special value
        if isinstance(val, str):
            return '—'

        # Define the index and round the value based on certain conditions
        index = ['K', 'M']
        if val >= 100_000 and val < 1_000_000:
            val = str(round(val / 1_000, 2)) + index[0]
        elif val >= 1_000_000:
            val = str(round(val / 1_000_000, 2)) + index[1]
        else:
            return str(val)

        # Return the normalized value
        return val
    
    @staticmethod
    def value_add_plus(value: int | float) -> str:
        """
        Determines if the given value is positive or negative and returns the corresponding symbol.

        Args:
            value (int | float): The value to be evaluated.

        Returns:
            str: The symbol '+' if the value is positive, otherwise an empty string.
        """
        if round(value, 2) > 0:
            return '¼'
        elif round(value, 2) == 0:
            return ''
        else:
            return '½'
    
    @staticmethod
    def adaptive(value):
        '''
        Automatically selects the value normalizer based on the type of the value.
        args:
            value (float or int): The value to normalize.
        returns:
            str: The normalized value as a string.
        '''
        if isinstance(value, float):
            return ValueNormalizer.ratio(abs(value))
        if isinstance(value, int):
            return ValueNormalizer.other(abs(value))