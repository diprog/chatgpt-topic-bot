from typing import Optional

from db.models import BaseModel

collection = 'user_settings'


class ChatGPTSettings:
    def __init__(self, temperature=1.0, top_p=1.0, presence_penalty=0.0, frequency_penalty=0.0):
        self.temperature = temperature
        self.top_p = top_p
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty


class UserSettings(BaseModel):
    def __init__(self, user_id: Optional[int] = None, chatgpt_settings: Optional[ChatGPTSettings] = None):
        super().__init__(user_id, collection)
        self.chatgpt_settings = chatgpt_settings or ChatGPTSettings()


async def get(user_id: int) -> UserSettings:
    return await UserSettings.get(collection, id=user_id) or UserSettings(user_id)
