from typing import Optional

from aiogram.types import Message

import constants
from bot.utils import is_main_admin
from db import DataFile

data = DataFile('settings')


class Settings:
    def __init__(self, topics: Optional[dict[int, int]] = None, bot_admins: Optional[list[int]] = None):
        self.group_threads = topics or {}
        self.bot_admins = bot_admins or []

    async def set_topic_for_group(self, group_id: int, topic_id: int):
        self.group_threads[group_id] = topic_id
        await data.write(self)

    def is_message_in_allowed_thread(self, message: Message) -> bool:
        print(self.group_threads)
        if thread_id := self.group_threads.get(message.chat.id):
            return thread_id == message.message_thread_id
        return False

    def is_bot_admin(self, user_id):
        return user_id in self.bot_admins or is_main_admin(user_id)

    async def remove_admin(self, user_id: int):
        self.bot_admins.remove(user_id)
        await data.write(self)

    async def add_admin(self, user_id: int):
        self.bot_admins.append(user_id)
        await data.write(self)


async def get() -> Settings:
    return await data.read() or Settings()
