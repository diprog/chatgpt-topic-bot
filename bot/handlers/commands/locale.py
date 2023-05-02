from aiogram.filters import Command
from aiogram.types import Message

import loc
from bot.filters import user_is_bot_admin
from bot import router


@router.message(Command('loc'))
async def command_locale_handler(message: Message) -> None:
    if not await user_is_bot_admin(message):
        return
    loc.clear()
    await loc.init()
    await message.answer(loc.loc('LOCALE_UPDATED_MSG'))
