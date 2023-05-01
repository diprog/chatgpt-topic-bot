from aiogram import Bot
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from aiogram.utils.web_app import check_webapp_signature, safe_parse_webapp_init_data
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from bot.webapp.templates import load_from_base_template

user_state = {}

routes = web.RouteTableDef()


@routes.get('/chatgpt_topic_bot/settings')
async def demo_handler(request: Request):
    return web.Response(text=load_from_base_template('settings.html'), content_type='text/html')


@routes.post('/chatgpt_topic_bot/checkData')
async def check_data_handler(request: Request):
    bot: Bot = request.app["bot"]

    data = await request.post()
    if check_webapp_signature(bot.token, data["_auth"]):
        return json_response({"ok": True})
    return json_response({"ok": False, "err": "Unauthorized"}, status=401)


@routes.post('/chatgpt_topic_bot/sendMessage')
async def send_message_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    print(data)
    reply_markup = None
    await bot.answer_web_app_query(
        web_app_query_id=web_app_init_data.query_id,
        result=InlineQueryResultArticle(
            id=web_app_init_data.query_id,
            title="Адрес",
            input_message_content=InputTextMessageContent(
                message_text=data['text'],
                parse_mode=None,
            ),
            reply_markup=reply_markup,
        ),
    )
    return json_response({"ok": True})


@routes.post('/chatgpt_topic_bot/initApp')
async def init_app(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    user_id = data['_unsafe_data[user][id]']
    if check_webapp_signature(bot.token, data["_auth"]):
        return json_response({'response': {"ok": True}})

    return json_response({"ok": False, "err": "Unauthorized"}, status=401)
