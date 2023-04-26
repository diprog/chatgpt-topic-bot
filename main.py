import asyncio
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(module)s %(funcName)s ~~~~ %(message)s')
from aiogram import Dispatcher

from bot import bot
from bot.router import router

dp = Dispatcher()


async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
