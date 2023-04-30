from typing import Optional

from aiogram.types import User

from db import BaseModel

collection = 'logging'


class Logging(BaseModel):
    def __init__(self,
                 user_threads: Optional[dict[int, int]] = None,
                 users: Optional[dict[int, User]] = None,
                 group_id: Optional[int] = None):
        super().__init__(0, collection)
        self.user_threads = user_threads or {}
        self.users = users or {}
        self.group_id = group_id

    def get_user_thread(self, user_id: int):
        return self.user_threads.get(user_id)

    async def set_group(self, group_id: int):
        self.user_threads = {}
        self.group_id = group_id
        await self.save()

    async def set_user_thread(self, user: User, message_thread_id: int):
        self.users[user.id] = user
        self.user_threads[user.id] = message_thread_id
        await self.save()


async def get() -> Logging:
    return await Logging.get(collection, id=0) or Logging()
