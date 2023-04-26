from typing import Optional

from db import DataFile

data = DataFile('user_contexts')


class Message:
    def __init__(self, content: str, role: str):
        self.content = content
        self.role = role

    def to_dict(self):
        return self.__dict__.copy()


class UserContext:
    def __init__(self, messages: Optional[list[Message]] = None):
        self.messages = messages or []

    def length(self):
        text_length = 0
        for message in self.messages:
            text_length += len(message.content)
        return text_length

    def add_message(self, content: str, role: str):
        self.messages.append(Message(content, role))

    def messages_dict(self):
        return [message.to_dict() for message in self.messages]


class UserContexts:
    def __init__(self, contexts: Optional[dict[int, UserContext]] = None):
        self.contexts = contexts or {}

    def context(self, user_id):
        try:
            return self.contexts[user_id]
        except KeyError:
            self.contexts[user_id] = UserContext()
            return self.contexts[user_id]

    async def add_message(self, user_id: int, content: str, role: str):
        self.context(user_id).add_message(content, role)
        await data.write(self)

    def length(self, user_id: int):
        return self.context(user_id).length()

    def messages_dict(self, user_id: int):
        return self.context(user_id).messages_dict()


async def get() -> UserContexts:
    return await data.read() or UserContexts()
