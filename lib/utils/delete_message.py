from typing import TYPE_CHECKING

from .functions import safe_delete_message

if TYPE_CHECKING:
    from aiogram.types import Message


class DeleteMessage:
    def __init__(self):
        self._data: list['Message'] = []
    
    def __add__(self, other):
        self._data.append(other)
    
    def append(self, message: 'Message'):
        self._data.append(message)
    
    async def clear(self):
        for message in self._data:
            await safe_delete_message(message)
        self._data = []
