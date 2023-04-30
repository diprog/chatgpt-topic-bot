from aiogram.filters import Command
from aiogram.types import Message

from bot.router import router
from locale import loc


@router.message(Command('help'))
async def command_start_handler(message: Message) -> None:
    await message.answer(loc('HELP_MSG'))
