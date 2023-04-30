from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ForceReply

import db
from bot.filters import user_is_bot_admin
from bot.router import router


class Form(StatesGroup):
    photo = State()


@router.message(Command('welcome_image'))
async def command_welcome_image(message: Message, state: FSMContext) -> None:
    if await user_is_bot_admin(message):
        await state.set_state(Form.photo)
        await message.answer('Отправьте фото', reply_markup=ForceReply())


@router.message(Form.photo, F.photo)
async def process_name(message: Message, state: FSMContext) -> None:
    settings = await db.settings.get()
    settings.welcome_image_file_id = message.photo[-1].file_id
    await settings.save()
    await state.clear()
    await message.answer('Фото для команды /start успешно обновлено.')
