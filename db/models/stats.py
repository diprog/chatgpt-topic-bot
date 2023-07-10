import time
from datetime import datetime

from db import database

collection = 'stats'


async def save(context: dict, openai_response: dict):
    data = {
        'context': context,
        'response': openai_response,
        'timestamp': time.time(),
        'datetime': datetime.now()
    }
    await database[collection].insert_one(data)
