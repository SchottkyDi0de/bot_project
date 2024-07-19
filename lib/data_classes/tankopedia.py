from typing import Literal
from pydantic import BaseModel, PositiveInt


class Tank(BaseModel):
    id: PositiveInt
    name: str
    tier: PositiveInt
    type: Literal['mediumTank', 'lightTank', 'heavyTank', 'AT-SPG', 'Unknown']
