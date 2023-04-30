from typing import Optional

from aiogram.types import User

from db import BaseModel

collection = 'admin_requests'


class UserData:
    def __init__(self, full_name, username: Optional[str] = None):
        self.full_name = full_name
        self.username = username


class AdminRequests(BaseModel):
    def __init__(self, users: Optional[dict[str | int, UserData]] = None):
        super().__init__(0, collection)
        self.users = users or {}

    async def add(self, user: User):
        self.users[user.id] = UserData(user.full_name, user.username)
        await self.save()

    async def delete(self, user_id):
        del self.users[user_id]
        await self.save()

    def get(self, user_id) -> UserData:
        return self.users.get(user_id)


async def get() -> AdminRequests:
    return await AdminRequests.get(collection, id=0) or AdminRequests()


async def add(user: User):
    admin_requests = await get()
    await admin_requests.add(user)
