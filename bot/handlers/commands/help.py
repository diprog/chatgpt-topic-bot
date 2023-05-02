from aiogram.filters import Command
from aiogram.types import Message

from bot import router
from locale import loc
from bot.inline_keyboards import help

@router.message(Command('help'))
async def command_start_handler(message: Message, base_url: str) -> None:
    await message.answer(loc('HELP_MSG'), reply_markup=help(base_url))
