from enum import Enum


class DivideReturnType(Enum):
    INTEGER = 1
    FLOAT = 2
    STRING = 3


def safe_divide(dividend: float | int, divisor: float | int, default: int | float = 0, return_type: DivideReturnType = DivideReturnType.FLOAT) -> float:
    """
    This function safely divides the dividend by the divisor.
    
    Args:
        dividend (float | int): The number to be divided.
        divisor (float | int): The number to divide by.
        default (int | float, optional): The default value to return if the divisor is zero. Defaults to 0.
        return_type (DivideReturnType, optional): The type of value to return. Defaults to DivideReturnType.FLOAT.
        
    Returns:
        float: The result of the division, rounded to the specified number of decimal places.
        
    Raises:
        TypeError: If the dividend or divisor is not a float or int, or if an unknown return type is specified.
    """
    if not isinstance(dividend, (int, float)):
        raise TypeError(f'Type of dividend must be float or int, but {type(dividend)} was given')
    if not isinstance(divisor, (int, float)):
        raise TypeError(f'Type of divisor must be float or int, but {type(divisor)} was given')
    
    res = dividend / divisor if divisor != 0  else default
    
    if return_type == DivideReturnType.INTEGER:
        return round(res)
    elif return_type == DivideReturnType.STRING:
        return str(res)
    elif return_type == DivideReturnType.FLOAT:
        return res if isinstance(res, float) else float(res)
    else:
        raise TypeError(f'Unknown return type: {return_type.__class__.__name__}')