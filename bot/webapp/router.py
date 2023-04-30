from pathlib import Path

from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    WebAppInfo,
)
from aiogram.utils.web_app import check_webapp_signature, safe_parse_webapp_init_data

import globals
import logic
import db
import constants
from fuzzywuzzy import fuzz
from aiohttp import web
user_state = {}

routes = web.RouteTableDef()

@routes.get('/settings')
async def demo_handler(request: Request):
    return web.Response(text=instructions[path], content_type='text/html')
    return FileResponse(Path(__file__).parent.resolve() / "bot/webapp//main.html")

@routes.get('/')
async def index_handler(request: Request):
    return FileResponse(Path(__file__).parent.resolve() / "index.html")


async def city_select_handler(request: Request):
    return FileResponse(Path(__file__).parent.resolve() / "city_select.html")


async def check_data_handler(request: Request):
    bot: Bot = request.app["bot"]

    data = await request.post()
    if check_webapp_signature(bot.token, data["_auth"]):
        return json_response({"ok": True})
    return json_response({"ok": False, "err": "Unauthorized"}, status=401)


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


async def search_address(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    user_id = data['_unsafe_data[user][id]']

    if check_webapp_signature(bot.token, data["_auth"]):
        user_data = await db.get_user_data(user_id)
        city_id = str(user_data.city_id)
        q = data['q'].lower()

        adresses = []
        adresses_dict = {}
        for street in constants.prepared_search[city_id].keys():
            for house in constants.prepared_search[city_id][street]:
                full_address = f'{street} {house}'
                adresses.append(full_address)
                adresses_dict[full_address] = (street, house)
        addresses_search = []
        for address in adresses:
            ratio = fuzz.token_sort_ratio(q, address.lower())
            if ratio > 60:
                addresses_search.append((ratio, address))
        search_suggestions = sorted(addresses_search, key=lambda x: x[0], reverse=True)
        result = []
        for search_suggestion in search_suggestions[:10]:
            address = adresses_dict[search_suggestion[1]]
            html = f'''<button id="main_btn" onclick="searchDoorcodes('{address[0]}', '{address[1]}');">{search_suggestion[1]}</button>'''
            result.append(html)
        if not result:
            result = 'Ничего не нашлось. Проверьте корректность ввода адреса.'
        stats = {'search_address': data['q']}
        await db.write_stats(user_id, stats)
        return json_response({'response': {"ok": True, "search_suggestions": result}})

    return json_response({"ok": False, "err": "Unauthorized"}, status=401)


def convert_to_int(obj):
    try:
        return int(obj)
    except:
        return -1


async def search_doorcodes(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    user_id = data['_unsafe_data[user][id]']
    if check_webapp_signature(bot.token, data["_auth"]):
        user_data = await db.get_user_data(user_id)
        city_id = user_data.city_id
        street = data['street']
        house = data['house']
        stats = {'search_doorcodes': {'city_id': city_id, 'street': street, 'house': house}}
        await db.write_stats(user_id, stats)
        houses = await db.find_address(city_id, street, house)
        filtered = {}
        for house in houses:
            if filtered.get(house['entrance']):
                if house['doorcode'] not in filtered[house['entrance']]:
                    filtered[house['entrance']].append(house['doorcode'])
            else:
                filtered[house['entrance']] = [house['doorcode']]
        filtered_tuples = list(filtered.items())
        parsed = []
        cant_parse = []
        for i, filtered_tuple in enumerate(filtered_tuples):
            filtered_tuples[i] = list(filtered_tuple)
            if filtered_tuple[0] is None:
                cant_parse.append(('нет', filtered_tuple[1]))
            else:
                try:
                    entrance_num = int(filtered_tuple[0])
                    parsed.append(entrance_num, filtered_tuples[1])
                except:
                    cant_parse.append(filtered_tuple)

        sorted_entrances = sorted(parsed, key=lambda item: item[0])
        text = '<table class="doorcodes"><tr><th>Подъезд</th><th>Коды</th</tr>'
        for entrances in sorted_entrances:
            text += f'<tr><th>{entrances[0]}</th><th>{", ".join(entrances[1])}</th></tr>'
        for entrances in cant_parse:
            text += f'<tr><th>{entrances[0]}</th><th>{", ".join(entrances[1])}</th></tr>'
        text += '</table>'
        return json_response({'response': {"ok": True, "doorcodes": text}})
    return json_response({"ok": False, "err": "Unauthorized"}, status=401)


async def init_app(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    user_id = data['_unsafe_data[user][id]']
    if check_webapp_signature(bot.token, data["_auth"]):
        user_data = await db.get_user_data(user_id)
        city = constants.cities_reversed[user_data.city_id]
        cities_names = []
        for city_id in constants.prepared_search.keys():
            city_id = int(city_id)
            cities_names.append(constants.cities_reversed[city_id])
        cities_names.sort()
        for i, city_name in enumerate(cities_names):
            cities_names[i] = f'''<a href="#" onclick="changeCity('{city_name}')">{city_name}</a>'''
        return json_response({'response': {"ok": True, "city": city, 'cities_names': cities_names}})

    return json_response({"ok": False, "err": "Unauthorized"}, status=401)


async def change_city(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    user_id = data['_unsafe_data[user][id]']
    city = data['city']
    if check_webapp_signature(bot.token, data["_auth"]):
        await db.update_user_data(user_id, 'city_id', constants.cities[city])
        return json_response({'response': {"ok": True}})

    return json_response({"ok": False, "err": "Unauthorized"}, status=401)
