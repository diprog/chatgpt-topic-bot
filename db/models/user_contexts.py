from typing import Optional

from db.models import BaseModel

collection = 'user_contexts'


class ContextMessage:
    def __init__(self, content: str, role: str):
        self.content = content
        self.role = role

    def to_dict(self):
        return dict(content=self.content, role=self.role)


class UserContext(BaseModel):
    def __init__(self, user_id: int, messages: Optional[list[ContextMessage]] = None):
        super().__init__(user_id, collection)
        self.messages = messages or []

    def length(self):
        text_length = 0
        for message in self.messages:
            text_length += len(message.content)
        return text_length

    def add_message(self, content: str, role: str):
        self.messages.append(ContextMessage(content, role))

    def messages_dict(self):
        return [message.to_dict() for message in self.messages]

    async def clear(self) -> bool:
        if self.messages:
            self.messages = []
            await self.save()
            return True
        return False


async def get(user_id: int) -> UserContext:
    return (await UserContext.get(collection, id=user_id)) or UserContext(user_id)


async def clear(user_id: int) -> bool:
    context = await get(user_id)
    return await context.clear()
