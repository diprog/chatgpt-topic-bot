from aiogram.filters import Command
from aiogram.types import Message

from bot import router


@router.message(Command('id'))
async def command_id(message: Message) -> None:
    await message.answer(str(message.from_user.id))
