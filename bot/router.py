import traceback

from aiogram import Router, types, Bot
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import Command

import constants
import db.admin_requests
import db.logging
import db.settings
import db.user_contexts
from bot import callback_data
from bot.inline_keyboards import admin_request, admins
from bot.utils import is_main_admin, prepare_markdown
from chatgpt import ChatGPT

router = Router()


async def topic_filter(message: types.Message, topic=True):
    if not message.chat.is_forum:
        await message.answer('❗️ Команда доступна только в группе с топиками.')
        return False

    settings = await db.settings.get()
    if not settings.is_bot_admin(message.from_user.id):
        await message.reply('❗️ Команда доступна только администрации бота.')
        return False

    chat_member = await message.chat.get_member(message.from_user.id)
    if not isinstance(chat_member, (types.ChatMemberOwner, types.ChatMemberAdministrator)):
        if message.sender_chat and message.sender_chat.id != message.chat.id:
            await message.reply('❗️ Команда доступна только владельцу группы.')
            return False
        await message.reply('❗️ Команда доступна только владельцу группы.')
        return False

    if not message.message_thread_id and topic:
        await message.reply('❗️ Команда может быть использована только внутри топика.')
        return False

    return True


async def send_logging_message(user: types.User, text: str) -> types.Message:
    bot = Bot.get_current()
    logging = await db.logging.get()
    if logging.group_id:
        if not logging.get_user_thread(user.id):
            forum_topic = await bot.create_forum_topic(logging.group_id, user.full_name)
            await logging.set_user_thread(user, forum_topic.message_thread_id)
        if thread_id := logging.get_user_thread(user.id):
            return await bot.send_message(logging.group_id, text, thread_id)


@router.message(Command('start'))
async def command_start_handler(message: types.Message) -> None:
    bot = Bot.get_current()
    settings = await db.settings.get()

    group_admin_commands = [
        types.BotCommand(command='/start', description='Обновить список команд.'),
        types.BotCommand(command='/set', description='Отвечать только в топике, в котором вы отправили эту команду.'),
        types.BotCommand(command='/logging', description='Выбрать эту группу для отправки истории сообщений.'),
    ]

    admin_commands_private = [
        types.BotCommand(command='/start', description='Обновить список команд.'),
        types.BotCommand(command='/admins', description='Управлять выданнами правами администратора.'),
    ]

    user_commands = [
        types.BotCommand(command='/clear', description='Очистить свой контекст.')
    ]

    if settings.is_bot_admin(message.from_user.id):
        await bot.set_my_commands(user_commands + admin_commands_private, types.BotCommandScopeChat(chat_id=message.from_user.id))

    await bot.set_my_commands(user_commands + group_admin_commands, types.BotCommandScopeAllChatAdministrators())
    await bot.set_my_commands(user_commands, types.BotCommandScopeAllGroupChats())
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
    await bot.send_message(constants.MAIN_ADMIN_ID,
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


@router.message(Command('clear'))
async def command_clear(message: types.Message) -> None:
    if await db.user_contexts.clear(message.from_user.id):
        await message.reply('🗑 Вы успешно очистили свой контекст.')
        await send_logging_message(message.from_user, '🗑 <i>Пользователь очистил свой контекст.</i>')
    else:
        await message.reply('Ваш контекст уже очищен.')


@router.message(Command('logging'))
async def command_logging(message: types.Message) -> None:
    if await topic_filter(message, topic=False):
        logging = await db.logging.get()
        await logging.set_group(message.chat.id)
        await message.reply('✅ Эта группа выбрана для логов.')


@router.message(Command('set'))
async def command_start_handler(message: types.Message) -> None:
    if await topic_filter(message):
        settings = await db.settings.get()
        await settings.set_topic_for_group(message.chat.id, message.message_thread_id)
        await message.reply('✅ Теперь бот будет работать внутри этого топика.')


@router.message()
async def any_message(message: types.Message) -> None:
    if not message.text or message.text.startswith('/'):
        return

    bot = Bot.get_current()
    user_id = message.from_user.id
    settings = await db.settings.get()
    if (message.message_thread_id and settings.is_message_in_allowed_thread(message)) or (
            settings.is_bot_admin(user_id) and message.chat.type == ChatType.PRIVATE):
        reply_message = await message.reply('🕑 Пожалуйста, подождите...')
        async with ChatGPT(constants.CHATGPT_KEY) as gpt:
            try:
                contexts = await db.user_contexts.get()
                print(contexts.length(user_id))
                answer = await gpt.completions(
                    contexts.messages_dict(user_id) + [dict(content=message.text, role='user')])
                await reply_message.edit_text(answer, parse_mode=None)
                await contexts.add_message(user_id, message.text, 'user')
                await contexts.add_message(user_id, answer, 'assistant')

                if user_message := await send_logging_message(message.from_user, '👤 ' + message.text):
                    await user_message.reply('🤖 ' + answer, parse_mode=None)
            except:
                await reply_message.edit_text(
                    '🔴 Произошла ошибка.\n\n<i>Попробуйте очистить свой контекст с помощью /clear.</i>')
                await bot.send_message(constants.DEVELOPER_ID, traceback.format_exc())
