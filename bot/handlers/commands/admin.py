from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import constants
import db.admin_requests
import db.logging
import db.settings
import db.user_contexts
from bot.callback_data import AdminRequestAnswer
from bot.inline_keyboards import admin_request
from bot.router import router


@router.message(Command('admin'))
async def command_admin(message: Message) -> None:
    user = message.from_user
    settings = await db.settings.get()
    if settings.is_bot_admin(user.id):
        await message.answer('✅ Вы уже являетесь администратором бота.')
        return

    bot = Bot.get_current()
    await bot.send_message(constants.MAIN_ADMIN_ID,
                           f'Пользователь <b>{user.full_name}</b> запросил права администратора.',
                           reply_markup=admin_request(user.id))
    await db.admin_requests.add(user)
    await message.answer('Вы отправили запрос на получение прав администратора.\nЖдите ответа.')


@router.callback_query(AdminRequestAnswer.filter())
async def admin_request_answer(query: CallbackQuery, callback_data: AdminRequestAnswer):
    bot = Bot.get_current()
    if callback_data.decline:
        await bot.send_message(callback_data.to_user_id, '⛔️ Ваш запрос на получение прав администратора был отклонен.')
        await query.message.edit_text(query.message.html_text + '\n\n<i>⛔️ Вы отклонили запрос.</i>', reply_markup=None)
    else:
        settings = await db.settings.get()
        await settings.add_admin(callback_data.to_user_id)
        await bot.send_message(callback_data.to_user_id, '✅ Ваш запрос на получение прав администратора был принят.')
        await query.message.edit_text(query.message.html_text + '\n\n<i>✅ Вы приняли запрос.</i>', reply_markup=None)
    await query.answer()
