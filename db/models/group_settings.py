from typing import Optional

from aiogram.types import Message

from db.models import BaseModel

collection = 'group_settings'


class GroupSettings(BaseModel):
    def __init__(self, group_id: Optional[int] = None, active_topic_id: Optional[int] = None):
        super().__init__(group_id, collection)
        self.active_topic_id = active_topic_id

    def is_message_in_allowed_thread(self, message: Message) -> bool:
        if self.active_topic_id:
            return self.active_topic_id == message.message_thread_id
        return False


async def get(group_id: int) -> GroupSettings:
    return await GroupSettings.get(collection, id=group_id) or GroupSettings(group_id)
