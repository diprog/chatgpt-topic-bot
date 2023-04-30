from aiogram.filters import Command
from aiogram.types import Message

import db.admin_requests
import db.logging
import db.settings
import db.user_contexts
from bot.handlers.methods import send_logging_message
from bot.router import router

@router.message(Command('clear'))
async def command_clear(message: Message) -> None:
    if await db.user_contexts.clear(message.from_user.id):
        await message.reply('🗑 Вы успешно очистили свой контекст.')
        await send_logging_message(message.from_user, '🗑 <i>Пользователь очистил свой контекст.</i>')
    else:
        await message.reply('Ваш контекст уже очищен.')
