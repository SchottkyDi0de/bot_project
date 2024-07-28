from typing import Literal
from pydantic import BaseModel


class Tank(BaseModel):
    id: int
    name: str
    tier: int
    type: Literal['mediumTank', 'lightTank', 'heavyTank', 'AT-SPG', 'Unknown']
