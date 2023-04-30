# from copy import copy
#
# import aiofiles
# import jsonpickle
#
# cache = {}
#
#
# class DataFile:
#     def __init__(self, filename: str):
#         self.path = f'db/data/{filename}.json'
#
#     def save_to_cache(self, obj):
#         global cache
#         cache[self.path] = obj
#
#     def read_from_cache(self):
#         global cache
#         try:
#             return copy(cache[self.path])
#         except KeyError:
#             return None
#
#     async def read(self):
#         global cache
#
#         if obj := self.read_from_cache():
#             return obj
#
#         try:
#             async with aiofiles.open(self.path, 'r', encoding='utf-8') as f:
#                 self.save_to_cache(jsonpickle.decode(await f.read(), keys=True))
#                 return self.read_from_cache()
#         except FileNotFoundError:
#             return None
#
#     async def write(self, obj):
#         async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:
#             self.save_to_cache(obj)
#             await f.write(jsonpickle.encode(obj, keys=True))
#
#
# def delete_cache(path):
#     try:
#         del cache[path]
#     except KeyError:
#         pass


from motor.motor_asyncio import AsyncIOMotorClient

from db import pickler

client = AsyncIOMotorClient('mongodb://212.192.9.160:27016/', username='admin', password='everesthero')
database = client.get_database('chatgpt_topic_bot')


class BaseModel:
    def __init__(self, id, collection: str):
        self.id = id
        self.collection = collection

    async def save(self):
        try:
            self.__delattr__('_id')
        except AttributeError:
            pass
        find_query = {'id': self.id}
        set_query = {'$set': pickler.flatten(self)}
        await database[self.collection].update_one(find_query, set_query, upsert=True)

    @staticmethod
    async def get(collection, **query):
        if document := await database[collection].find_one(query):
            obj = pickler.restore(document)
            obj.collection = collection
            return obj


def get_collection(collection):
    return database.get_collection(collection)

from typing import Optional

from aiogram.types import Message

from db import BaseModel

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
