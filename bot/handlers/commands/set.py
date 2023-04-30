from aiogram.filters import Command
from aiogram.types import Message

import db.admin_requests
import db.logging
import db.settings
import db.user_contexts
from bot.handlers.methods import topic_filter
from bot.router import router


@router.message(Command('set'))
async def command_start_handler(message: Message) -> None:
    if await topic_filter(message):
        settings = await db.settings.get()
        await settings.set_topic_for_group(message.chat.id, message.message_thread_id)
        await message.reply('✅ Теперь бот будет работать внутри этого топика.')
