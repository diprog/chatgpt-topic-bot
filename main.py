import asyncio
import logging
import ssl
import traceback
from pathlib import Path

from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web
from aiohttp.web import _run_app
from aiohttp.web_app import Application

import constants
import imports
import loc
from bot import router
from bot.middlewares import error_middleware, save_update_to_db_middleware
from bot.webapp.router import routes



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

    await loc.init()

    bot = Bot(constants.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp["base_url"] = 'https://chatgpt-topic-bot.diprog.ru/webapp'
    dp.startup.register(on_startup)
    dp.include_router(router)
    # await dp.start_polling(bot)

    app = Application()
    app["bot"] = bot

    app.add_routes([web.static('/webapp/css', Path(__file__).parent.resolve() / 'bot/webapp/html/css')])
    app.add_routes(routes)
    setup_application(app, dp, bot=bot)
    try:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain('/etc/letsencrypt/live/chatgpt-topic-bot.diprog.ru/fullchain.pem',
                                    '/etc/letsencrypt/live/chatgpt-topic-bot.diprog.ru/privkey.pem')
        await _run_app(app, host="0.0.0.0", port=443, ssl_context=ssl_context)
    except:
        print(traceback.format_exc())
        await _run_app(app, host="0.0.0.0", port=80)


if __name__ == "__main__":
    asyncio.run(main())
