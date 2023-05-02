from aiogram.filters import Command
from aiogram.types import Message

from bot import router
from bot.inline_keyboards import user_settings
from loc import loc


@router.message(Command(commands=['settings']))
async def command_settings_handler(message: Message, base_url: str):
    await message.answer(loc('SETTINGS_COMMAND_MSG'), reply_markup=user_settings(base_url))
