from typing import Optional

from pydantic import BaseModel


class Achievements(BaseModel):
    mainGun: Optional[int | str] = None
    medalRadleyWalters: Optional[int | str] = None
    markOfMastery: Optional[int | str] = None
    medalKolobanov: Optional[int | str] = None
    warrior: Optional[int | str] = None