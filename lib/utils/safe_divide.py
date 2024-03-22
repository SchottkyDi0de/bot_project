def safe_divide(dividend: float | int, divisor: float | int) -> float:
    '''
    This function safely divides dividend by divisor
    if divisor is 0, returns 0.0 (float)
    
    args:
        dividend: int | float
        divisor: int | float
        
    returns:
        float
        
    raises:
        TypeError
    '''
    if not isinstance(dividend, (int, float)):
        raise TypeError(f'Type of dividend must be float or int, but {type(dividend)} was given')
    if not isinstance(divisor, (int, float)):
        raise TypeError(f'Type of divisor must be float or int, but {type(divisor)} was given')
        
    if divisor == 0:
        return 1.0
    else:
        return dividend / divisor