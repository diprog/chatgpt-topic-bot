from aiogram.filters import Command
from aiogram.types import Message

import locale
from bot.filters import user_is_bot_admin
from bot.router import router


@router.message(Command('locale'))
async def command_locale_handler(message: Message) -> None:
    if not await user_is_bot_admin(message):
        return
    locale.clear()
    await locale.init()
    await message.answer(locale.loc('LOCALE_UPDATED_MSG'))
