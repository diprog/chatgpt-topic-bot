import json
import traceback
from typing import Callable, Any, Awaitable

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Update, BufferedInputFile

import constants
import db
from bot.utils import prepare_markdown


async def save_update_to_db_middleware(
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any]
) -> Any:
    await db.updates.save(event.dict())


async def error_middleware(
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any]
) -> Any:
    try:
        return await handler(event, data)
    except:
        bot = Bot.get_current()
        if event.message:
            reply_method = event.message.reply if event.message.chat.id < 0 else event.message.answer
            await reply_method('🔴 Произошла ошибка.')

            message = await bot.send_message(constants.DEVELOPER_ID, '🔴 *Ошибка.*')

            message_json = json.dumps(event.message.json())
            text = prepare_markdown(message_json)
            try:
                await message.reply(f'💬 Сообщение:\n```\n{text}\n```', parse_mode=ParseMode.MARKDOWN_V2)
            except TelegramBadRequest as e:
                if 'message is too long' in e.message:
                    text_file = BufferedInputFile(message_json.encode('utf-8'), filename='message.json')
                    await message.reply_document(text_file)

            error = traceback.format_exc()
            error_text = prepare_markdown(error)
            error_text = f'📜 Текст ошибки:\n```\n{error_text}\n```'
            try:
                await message.reply(error_text, parse_mode=ParseMode.MARKDOWN_V2)
            except TelegramBadRequest as e:
                if 'message is too long' in e.message:
                    text_file = BufferedInputFile(error.encode('utf-8'), filename='traceback.txt')
                    await message.reply_document(text_file)
