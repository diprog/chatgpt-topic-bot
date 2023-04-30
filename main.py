import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode

import constants
import imports
import locale
from bot.middlewares import error_middleware
from bot.router import router

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(module)s %(funcName)s ~~~~ %(message)s')

dp = Dispatcher()


@dp.update.outer_middleware()
async def _(*args, **kwargs):
    return await error_middleware(*args, **kwargs)


async def main() -> None:
    imports.import_all('bot.handlers')
    imports.import_all('bot.handlers.commands')
    imports.import_all('bot.handlers.other')
    await locale.init()
    bot = Bot(constants.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
