from typing import Optional

from bot.utils import is_main_admin
from db import BaseModel

collection = 'settings'


class Settings(BaseModel):
    def __init__(self, bot_admins: Optional[list[int]] = None):
        super().__init__(0, collection)
        self.bot_admins = bot_admins or []

    def is_bot_admin(self, user_id):
        return user_id in self.bot_admins or is_main_admin(user_id)

    async def remove_admin(self, user_id: int):
        self.bot_admins.remove(user_id)
        await self.save()

    async def add_admin(self, user_id: int):
        self.bot_admins.append(user_id)
        await self.save()


async def get() -> Settings:
    return await Settings.get(collection, id=0) or Settings()
