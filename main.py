import asyncio
import logging
from pathlib import Path

from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web
from aiohttp.web import run_app, _run_app
from aiohttp.web_app import Application
from bot.webapp.router import routes
import constants
import imports
import locale
from bot.middlewares import error_middleware, save_update_to_db_middleware
from bot import router

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(module)s %(funcName)s ~~~~ %(message)s')

dp = Dispatcher()


@dp.update.outer_middleware()
async def _(*args, **kwargs):
    await save_update_to_db_middleware(*args, **kwargs)
    return await error_middleware(*args, **kwargs)

async def on_startup(bot: Bot, base_url: str, dispatcher: Dispatcher):
    await bot.delete_webhook()
    asyncio.create_task(dispatcher.start_polling(bot, base_url=base_url))

async def main() -> None:
    imports.import_all('bot.handlers')
    imports.import_all('bot.handlers.commands')
    imports.import_all('bot.handlers.other')
    await locale.init()

    bot = Bot(constants.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp["base_url"] = 'https://a271-5-228-139-107.ngrok-free.app/chatgpt_topic_bot'
    dp.startup.register(on_startup)
    dp.include_router(router)
    # await dp.start_polling(bot)

    app = Application()
    app["bot"] = bot

    app.add_routes([web.static('/chatgpt_topic_bot/css', Path(__file__).parent.resolve() / 'bot/webapp/html/css')])
    app.add_routes(routes)
    setup_application(app, dp, bot=bot)
    await _run_app(app, host="0.0.0.0", port=80)


if __name__ == "__main__":
    asyncio.run(main())
