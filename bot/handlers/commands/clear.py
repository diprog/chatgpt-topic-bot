from aiogram.filters import Command
from aiogram.types import Message

import db.admin_requests
import db.logging
import db.settings
import db.user_contexts
from bot.handlers.methods import send_logging_message
from bot.router import router
from locale import loc


@router.message(Command('clear'))
async def command_clear(message: Message) -> None:
    context = await db.user_contexts.get(message.from_user.id)
    if await context.clear():
        await message.reply(loc('CONTEXT_CLEARED_MSG'))
        await send_logging_message(message.from_user, loc('CONTEXT_CLEARED_LOGGING_MSG'))
    else:
        await message.reply(loc('CONTEXT_ALREADY_CLEARED_MSG'))
