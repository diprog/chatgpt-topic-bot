from aiogram.filters import Command
from aiogram.types import Message

import db.admin_requests
import db.logging
import db.settings
import db.user_contexts
from bot.handlers.methods import topic_filter
from bot.router import router


@router.message(Command('logging'))
async def command_logging(message: Message) -> None:
    if await topic_filter(message, topic=False):
        logging = await db.logging.get()
        await logging.set_group(message.chat.id)
        await message.reply('✅ Эта группа выбрана для логов.')
