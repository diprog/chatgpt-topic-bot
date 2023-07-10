from motor.motor_asyncio import AsyncIOMotorClient

from db import pickler

client = AsyncIOMotorClient('mongodb://212.192.9.160:27016/', username='admin', password='everesthero')
database = client.get_database('chatgpt_topic_bot')

from .models import admin_requests
from .models import group_settings
from .models import logging
from .models import settings
from .models import updates
from .models import user_contexts
from .models import user_settings
from .models import stats
