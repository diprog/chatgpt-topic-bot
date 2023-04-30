from aiogram.filters import Command
from aiogram.types import Message

import db.group_settings
from bot.filters import topic_filter
from bot.router import router


@router.message(Command('set'))
async def command_start_handler(message: Message) -> None:
    if await topic_filter(message):
        group_settings = await db.group_settings.get(message.chat.id)
        group_settings.active_topic_id = message.message_thread_id
        await group_settings.save()
        await message.reply('✅ Теперь бот будет работать внутри этого топика.')
