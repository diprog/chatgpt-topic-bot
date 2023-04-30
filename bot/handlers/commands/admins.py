from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import db.admin_requests
import db.logging
import db.settings
import db.user_contexts
from bot.router import router
from bot.callback_data import AdminRemove
from bot.inline_keyboards import admins
from bot.utils import is_main_admin
from locale import loc


async def get_admins_text():
    settings = await db.settings.get()
    return loc('CHOOSE_ADMIN_TO_REMOVE_MSG') if settings.bot_admins else loc('NO_ADMINS_FOUND_MSG')


@router.message(Command('admins'))
async def command_admins(message: Message) -> None:
    if not is_main_admin(message.from_user.id):
        await message.reply('❗️ Команда доступна только главному администратору бота.')
        return
    await message.answer(await get_admins_text(), reply_markup=await admins())


@router.callback_query(AdminRemove.filter())
async def admin_remove(query: CallbackQuery, callback_data: AdminRemove):
    settings = await db.settings.get()
    await settings.remove_admin(callback_data.user_id)
    await Bot.get_current().send_message(callback_data.user_id, loc('ADMIN_RIGHTS_REMOVED_MSG'))
    await query.message.edit_text(await get_admins_text(), reply_markup=await admins())
