from aiogram.filters import Command
from aiogram.types import Message

import db
from bot.filters import topic_filter
from bot import router


@router.message(Command('logging'))
async def command_logging(message: Message) -> None:
    if await topic_filter(message, topic=False):
        logging = await db.logging.get()
        await logging.set_group(message.chat.id)
        await message.reply('✅ Эта группа выбрана для логов.')
