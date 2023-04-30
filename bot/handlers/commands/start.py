from aiogram.filters import Command
from aiogram.types import Message

from bot.handlers.methods import update_commands
from bot.router import router
from locale import loc


@router.message(Command('start'))
async def command_start_handler(message: Message) -> None:
    await message.answer(loc('START_MSG'))
    await update_commands(message.from_user.id)
