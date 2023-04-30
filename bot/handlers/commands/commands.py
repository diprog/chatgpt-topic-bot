from aiogram.filters import Command
from aiogram.types import Message

from bot.handlers.methods import update_commands
from bot import router


@router.message(Command('commands'))
async def command_commands_handler(message: Message) -> None:
    await update_commands(message.from_user.id)
