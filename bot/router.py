import traceback

from aiogram import Router, types, Bot
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeChat

import constants
import db.admin_requests
import db.settings
import db.user_contexts
from bot import callback_data
from bot.inline_keyboards import admin_request, admins
from bot.utils import is_main_admin
from chatgpt import ChatGPT

router = Router()


@router.message(Command('start'))
async def command_start_handler(message: types.Message) -> None:
    settings = await db.settings.get()
    if settings.is_bot_admin(message.from_user.id):
        commands = [
            BotCommand(command='/start', description='Обновить список команд.'),
            BotCommand(command='/admins', description='Управлять выданными правами администратора.'),
            BotCommand(command='/set', description='Отвечать только в топике, в котором вы отправили эту команду.')
        ]
        await Bot.get_current().set_my_commands(commands, BotCommandScopeChat(chat_id=message.from_user.id))
    await message.answer('Список команд обновлен.')


@router.message(Command('id'))
async def command_id(message: types.Message) -> None:
    await message.answer(str(message.from_user.id))


@router.message(Command('admin'))
async def command_admin(message: types.Message) -> None:
    user = message.from_user
    settings = await db.settings.get()
    if settings.is_bot_admin(user.id):
        await message.answer('✅ Вы уже являетесь администратором бота.')
        return

    bot = Bot.get_current()
    await bot.send_message(constants.DEVELOPER_ID,
                           f'Пользователь <b>{user.full_name}</b> запросил права администратора.',
                           reply_markup=admin_request(user.id))
    await db.admin_requests.add(user)
    await message.answer('Вы отправили запрос на получение прав администратора.\nЖдите ответа.')


@router.callback_query(callback_data.AdminRequestAnswer.filter())
async def admin_request_answer(query: types.CallbackQuery, callback_data: callback_data.AdminRequestAnswer):
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


async def get_admins_text():
    settings = await db.settings.get()
    return 'Выберите пользователя, которого нужно удалить из администраторов.' if settings.bot_admins else '❌ У бота нет дополнительных администраторов.\n\n<i>Вы можете попросить пользователя отправить вам запрос на получение прав администратора с помощью команды /admin.</i>'


@router.message(Command('admins'))
async def command_admins(message: types.Message) -> None:
    if not is_main_admin(message.from_user.id):
        await message.reply('❗️ Команда доступна только главному администратору бота.')
        return
    await message.answer(await get_admins_text(), reply_markup=await admins())


@router.callback_query(callback_data.AdminRemove.filter())
async def admin_remove(query: types.CallbackQuery, callback_data: callback_data.AdminRemove):
    settings = await db.settings.get()
    await settings.remove_admin(callback_data.user_id)
    await Bot.get_current().send_message(callback_data.user_id, 'Вы были лишены прав администратора.')
    await query.message.edit_text(await get_admins_text(), reply_markup=await admins())


@router.message(Command('set'))
async def command_start_handler(message: types.Message) -> None:
    if not message.chat.is_forum:
        await message.answer('❗️ Команда доступна только в группе с топиками.')
        return

    settings = await db.settings.get()
    if not settings.is_bot_admin(message.from_user.id):
        await message.reply('❗️ Команда доступна только администрации бота.')
        return

    if not isinstance(await message.chat.get_member(message.from_user.id),
                      (types.ChatMemberOwner, types.ChatMemberAdministrator)):
        if not is_main_admin(message.from_user.id):
            await message.reply('❗️ Команда доступна только владельцу группы.')
            return

    if not message.message_thread_id:
        await message.reply('❗️ Команда может быть использована только внутри топика.')
        return

    await settings.set_topic_for_group(message.chat.id, message.message_thread_id)
    await message.reply('✅ Теперь бот будет работать внутри этого топика.')


@router.message()
async def any_message(message: types.Message) -> None:
    if not message.text or message.text.startswith('/'):
        return

    user_id = message.from_user.id
    settings = await db.settings.get()
    if (message.message_thread_id and settings.is_message_in_allowed_thread(message)) or (
            settings.is_bot_admin(user_id) and message.chat.type == ChatType.PRIVATE):
        reply_message = await message.reply('🕑 Пожалуйста, подождите...')
        async with ChatGPT('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') as gpt:
            try:
                contexts = await db.user_contexts.get()
                print(contexts.length(user_id))
                answer = await gpt.completions(contexts.messages_dict(user_id) + [dict(content=message.text, role='user')])
                await reply_message.edit_text(answer)
                await contexts.add_message(user_id, message.text, 'user')
                await contexts.add_message(user_id, answer, 'assistant')
            except:
                await reply_message.edit_text('🔴 Произошла ошибка.')
                await Bot.get_current().send_message(constants.DEVELOPER_ID, traceback.format_exc())
