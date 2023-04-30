import asyncio
import logging

from aiogram import Dispatcher, Bot

import constants
import locale
from bot.router import router

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(module)s %(funcName)s ~~~~ %(message)s')

dp = Dispatcher()


async def main() -> None:
    locale.init()
    bot = Bot(constants.TELEGRAM_BOT_TOKEN, parse_mode='HTML')
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
