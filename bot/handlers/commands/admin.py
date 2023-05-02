from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import constants
import db
from bot.callback_data import AdminRequestAnswer
from bot.inline_keyboards import admin_request
from bot import router
from loc import loc


@router.message(Command('admin'))
async def command_admin(message: Message) -> None:
    user = message.from_user
    settings = await db.settings.get()
    if settings.is_bot_admin(user.id):
        await message.answer(loc('ALREADY_AN_ADMIN_MSG'))
        return

    bot = Bot.get_current()
    await bot.send_message(constants.MAIN_ADMIN_ID,
                           loc('ADMIN_PERMISSIONS_REQUEST_MSG', user.full_name),
                           reply_markup=admin_request(user.id))
    await db.admin_requests.add(user)
    await message.answer(loc('ADMIN_PERMISSIONS_REQUEST_SENT_MSG'))


@router.callback_query(AdminRequestAnswer.filter())
async def admin_request_answer(query: CallbackQuery, callback_data: AdminRequestAnswer):
    bot = Bot.get_current()
    if callback_data.decline:
        await bot.send_message(callback_data.to_user_id, loc('ADMIN_PERMISSIONS_REQUEST_DECLINED_MSG'))
        await query.message.edit_text(query.message.html_text + '\n\n<i>⛔️ Вы отклонили запрос.</i>', reply_markup=None)
    else:
        settings = await db.settings.get()
        await settings.add_admin(callback_data.to_user_id)
        await bot.send_message(callback_data.to_user_id, loc('ADMIN_PERMISSIONS_REQUEST_ACCEPTED_MSG'))
        await query.message.edit_text(query.message.html_text + '\n\n<i>✅ Вы приняли запрос.</i>', reply_markup=None)
    await query.answer()
