import traceback

from aiogram import types, Bot
from aiogram.enums import ChatType, ParseMode
from aiogram.exceptions import TelegramBadRequest

import constants
import db
from bot.handlers.methods import send_logging_message
from bot.router import router
from bot.utils import prepare_markdown
from chatgpt import ChatGPT
from locale import loc


@router.message()
async def any_message(message: types.Message) -> None:
    if not message.text or message.text.startswith('/'):
        return

    if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
        return

    bot = Bot.get_current()
    user_id = message.from_user.id
    settings = await db.settings.get()
    group_settings = await db.group_settings.get(message.chat.id)
    if not ((message.message_thread_id and group_settings.is_message_in_allowed_thread(message)) or (
            settings.is_bot_admin(user_id) and message.chat.type == ChatType.PRIVATE)):
        return

    reply_message = await message.reply('🕑 Пожалуйста, подождите...')
    context = await db.user_contexts.get(user_id)
    async with ChatGPT(constants.CHATGPT_KEY) as gpt:
        answer = await gpt.completions(
            context.messages_dict() + [dict(content=message.text, role='user')],
            temperature=0.7,
            presence_penalty=0.5,
            frequency_penalty=0.5,
            top_p=0.5
        )
        await reply_message.edit_text(answer, parse_mode=None)
        context.add_message(message.text, 'user')
        context.add_message(answer, 'assistant')
        await context.save()

        if user_message := await send_logging_message(message.from_user, '👤 ' + message.text):
            text = '🤖 ' + answer
            try:
                await user_message.reply(text, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest as e:
                if 'entities' in e.message:
                    await user_message.reply(text, parse_mode=None)
