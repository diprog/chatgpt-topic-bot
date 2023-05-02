from aiogram import Bot
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from aiogram.utils.web_app import check_webapp_signature, safe_parse_webapp_init_data
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

import db
from bot.webapp.templates import load_from_base_template

user_state = {}

routes = web.RouteTableDef()


@routes.get('/chatgpt_topic_bot/settings')
async def settings_handler(request: Request):
    return web.Response(text=load_from_base_template('settings.html'), content_type='text/html')


@routes.get('/chatgpt_topic_bot/bot_setup')
async def bot_setup_handler(request: Request):
    return web.Response(text=load_from_base_template('bot_setup.html'), content_type='text/html')

@routes.get('/chatgpt_topic_bot/gpt4')
async def bot_setup_handler(request: Request):
    return web.Response(text=load_from_base_template('gpt4.html'), content_type='text/html')

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


@routes.post('/chatgpt_topic_bot/getUserChatGPTSettings')
async def send_message_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
        user_settings = await db.user_settings.get(web_app_init_data.user.id)
        print(user_settings.__dict__)
        response = dict(ok=True, **user_settings.chatgpt_settings.__dict__)
        print(response)
        return json_response(response, status=200)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)


@routes.post('/chatgpt_topic_bot/saveUserChatGPTSettings')
async def send_message_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
        user_settings = await db.user_settings.get(web_app_init_data.user.id)
        user_settings.chatgpt_settings.temperature = data['settings[temperature]']
        user_settings.chatgpt_settings.top_p = data['settings[top_p]']
        user_settings.chatgpt_settings.presence_penalty = data['settings[presence_penalty]']
        user_settings.chatgpt_settings.frequency_penalty = data['settings[frequency_penalty]']
        await user_settings.save()
        return json_response(dict(ok=True), status=200)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
