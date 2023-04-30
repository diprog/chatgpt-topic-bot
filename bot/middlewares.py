import json
import traceback
from typing import Callable, Any, Awaitable

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import Update

import constants
from bot.utils import prepare_markdown


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
            message_json = prepare_markdown(json.dumps(event.message.json()))
            error = traceback.format_exc()
            message = await bot.send_message(constants.DEVELOPER_ID, '🔴 *Ошибка.*')
            await message.reply(f'💬 Сообщение:\n```\n{message_json}\n```', parse_mode=ParseMode.MARKDOWN_V2)
            await message.reply(f'📜 Текст ошибки:\n```\n{error}\n```', parse_mode=ParseMode.MARKDOWN_V2)
