from aiogram import types, Bot
from aiogram.exceptions import TelegramForbiddenError

import db.logging
import db.settings


async def update_commands(user_id: int):
    bot = Bot.get_current()

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

    settings = await db.settings.get()
    if settings.is_bot_admin(user_id):
        await bot.set_my_commands(user_commands + admin_commands_private,
                                  types.BotCommandScopeChat(chat_id=user_id))

    await bot.set_my_commands(user_commands + group_admin_commands, types.BotCommandScopeAllChatAdministrators())
    await bot.set_my_commands(user_commands, types.BotCommandScopeAllGroupChats())


async def send_logging_message(user: types.User, text: str) -> types.Message:
    bot = Bot.get_current()
    logging = await db.logging.get()
    if logging.group_id:
        try:
            if not logging.get_user_thread(user.id):
                forum_topic = await bot.create_forum_topic(logging.group_id, user.full_name)
                await logging.set_user_thread(user, forum_topic.message_thread_id)
            if thread_id := logging.get_user_thread(user.id):
                return await bot.send_message(logging.group_id, text, thread_id, parse_mode=None)
        except TelegramForbiddenError as e:
            # aiogram.exceptions.TelegramForbiddenError:
            # Telegram server says Forbidden: bot was kicked from the supergroup chat
            if 'kicked' in e.message:
                print('kicked')


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
