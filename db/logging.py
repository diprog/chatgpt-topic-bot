from typing import Optional

from aiogram.types import User

from db import DataFile

data = DataFile('logging')


class Logging:
    def __init__(self,
                 user_threads: Optional[dict[int, int]] = None,
                 users: Optional[dict[int, User]] = None,
                 group_id: Optional[int] = None):
        self.user_threads = user_threads or {}
        self.users = users or {}
        self.group_id = group_id

    def get_user_thread(self, user_id: int):
        return self.user_threads.get(user_id)

    async def set_group(self, group_id: int):
        self.user_threads = {}
        self.group_id = group_id
        await data.write(self)

    async def set_user_thread(self, user: User, message_thread_id: int):
        self.users[user.id] = user
        self.user_threads[user.id] = message_thread_id
        await data.write(self)


async def get() -> Logging:
    return await data.read() or Logging()
