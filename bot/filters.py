from aiogram import types

import db


async def chat_is_forum(message: types.Message) -> bool:
    if not message.chat.is_forum:
        await message.answer('❗️ Команда доступна только в группе с топиками.')
        return False
    return True


async def user_is_bot_admin(message: types.Message) -> bool:
    settings = await db.settings.get()
    if not settings.is_bot_admin(message.from_user.id):
        await message.reply('❗️ Команда доступна только администрации бота.')
        return False
    return True


async def user_is_group_admin(message: types.Message) -> bool:
    chat_member = await message.chat.get_member(message.from_user.id)
    if not isinstance(chat_member, (types.ChatMemberOwner, types.ChatMemberAdministrator)):
        if message.sender_chat and message.sender_chat.id != message.chat.id:
            await message.reply('❗️ Команда доступна только владельцу группы.')
            return False
        await message.reply('❗️ Команда доступна только владельцу группы.')
        return False
    return True


async def message_is_in_topic(message: types.Message, topic=True):
    if not message.message_thread_id and topic:
        await message.reply('❗️ Команда может быть использована только внутри темы.')
        return False
    return True


async def topic_filter(message: types.Message, topic=True):
    if not await chat_is_forum(message):
        return False

    if not await user_is_group_admin(message):
        return False

    if not await message_is_in_topic(message, topic):
        return False

    return True
