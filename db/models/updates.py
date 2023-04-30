from db import database

collection = 'updates'


async def save(update: dict):
    await database[collection].insert_one(update)
