import asyncio

from aiogram import types, Bot
from aiogram.enums import ChatType, ParseMode
from aiogram.exceptions import TelegramBadRequest

import constants
import db
from bot import router
from bot.handlers.methods import send_logging_message
from chatgpt import ChatGPT
from db.models.user_contexts import ContextMessage
from loc import loc


async def loading_message_updater(message: types.Message):
    emojis = '🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛'
    emoji_index = 1
    string_index = 2
    dots = '.'
    while True:
        await asyncio.sleep(3)
        try:
            emoji = emojis[emoji_index]
        except IndexError:
            emoji_index = 0
            emoji = emojis[emoji_index]
        await message.edit_text(emoji + ' ' + loc('PROCESSING_MSG') + dots)
        string_index += 1
        emoji_index += 1
        dots += '.'


@router.message()
async def any_message(message: types.Message) -> None:
    if not message.text or message.text.startswith('/'):
        return

    if message.message_thread_id and message.reply_to_message and message.reply_to_message.message_id != message.message_thread_id:
        if not message.reply_to_message.from_user.is_bot:
            return

    bot = Bot.get_current()
    user_id = message.from_user.id
    settings = await db.settings.get()
    group_settings = await db.group_settings.get(message.chat.id)
    if not ((message.message_thread_id and group_settings.is_message_in_allowed_thread(message)) or (
            settings.is_bot_admin(user_id) and message.chat.type == ChatType.PRIVATE)):
        return

    # Наконец-то закончились проверки.
    reply_message = await message.reply('🕐 ' + loc('PROCESSING_MSG'))
    # task = asyncio.create_task(loading_message_updater(reply_message))
    context = await db.user_contexts.get(user_id)
    user_settings = await db.user_settings.get(user_id)
    chatgpt_user_settings = user_settings.chatgpt_settings
    async with ChatGPT(constants.CHATGPT_KEY) as gpt:
        response = await gpt.completions(
            context.messages + [ContextMessage(message.text, 'user')],
            temperature=chatgpt_user_settings.temperature,
            presence_penalty=chatgpt_user_settings.presence_penalty,
            frequency_penalty=chatgpt_user_settings.frequency_penalty,
            top_p=chatgpt_user_settings.top_p
        )

        if error := response.get('error'):
            if error['code'] == 'context_length_exceeded':
                await reply_message.edit_text(loc('GPT_REPLY_ERROR_MSG'))
            else:
                await reply_message.edit_text('🔴 Произошла ошибка.\n\n' + error['message'])
            return

        answer = response['choices'][0]['message']['content']
        # task.cancel()

        # Если ответ превышает максимальный размер текста сообщения,
        # то делим ответ на отдельные части и отправляем по каждой части отдельное сообщение.
        if len(answer) <= 4096:
            await reply_message.edit_text(answer, parse_mode=None)
        else:
            chunks = [answer[i:i + 4096] for i in range(0, len(answer), 4096)]
            await reply_message.edit_text(chunks.pop(0), parse_mode=None)
            for chunk in chunks:
                await reply_message.reply(chunk, parse_mode=None)

        # Сохраняем историю сообщений в контекст пользователя.
        context.add_message(message.text, 'user')
        context.add_message(answer, 'assistant')
        await context.save()

        # И сохраняем историю сообщений в отдельную группу для логов.
        if user_message := await send_logging_message(message.from_user, '👤 ' + message.text):
            text = '🤖 ' + answer
            try:
                await user_message.reply(text, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest as e:
                if 'entities' in e.message:
                    await user_message.reply(text, parse_mode=None)
