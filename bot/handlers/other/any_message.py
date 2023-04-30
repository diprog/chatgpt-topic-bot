import traceback

from aiogram import types, Bot
from aiogram.enums import ChatType

import constants
import db.admin_requests
import db.logging
import db.settings
import db.user_contexts
from bot.handlers.methods import send_logging_message
from bot.router import router
from chatgpt import ChatGPT


@router.message()
async def any_message(message: types.Message) -> None:
    if not message.text or message.text.startswith('/'):
        return

    if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
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
                    contexts.messages_dict(user_id) + [dict(content=message.text, role='user')],
                    temperature=0.7,
                    presence_penalty=0.5,
                    frequency_penalty=0.5,
                    top_p=0.5
                )
                await reply_message.edit_text(answer, parse_mode=None)
                await contexts.add_message(user_id, message.text, 'user')
                await contexts.add_message(user_id, answer, 'assistant')

                if user_message := await send_logging_message(message.from_user, '👤 ' + message.text):
                    await user_message.reply('🤖 ' + answer, parse_mode=None)
            except:
                await reply_message.edit_text(
                    '🔴 Произошла ошибка.\n\n<i>Попробуйте очистить свой контекст с помощью /clear.</i>')
                await bot.send_message(constants.DEVELOPER_ID, traceback.format_exc())
