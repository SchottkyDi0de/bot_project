from typing import Optional

from pydantic import BaseModel


class Achievements(BaseModel):
    mainGun: Optional[int] = None
    medalRadleyWalters: Optional[int] = None
    markOfMastery: Optional[int] = None
    medalKolobanov: Optional[int] = None
    warrior: Optional[int] = None