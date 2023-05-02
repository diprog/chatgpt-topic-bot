from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

import db
from bot import callback_data


def InlineKeyboard(*rows):
    return InlineKeyboardMarkup(inline_keyboard=rows)


def InlineButton(text, callback=None):
    if callback:
        return InlineKeyboardButton(text=text, callback_data=callback.pack())
    else:
        return InlineKeyboardButton(text=text, callback_data='none')


def admin_request(to_user_id: int):
    return InlineKeyboard(
        [
            InlineButton('✅ Принять', callback_data.AdminRequestAnswer(decline=False, to_user_id=to_user_id)),
            InlineButton('⛔️ Отклонить', callback_data.AdminRequestAnswer(decline=True, to_user_id=to_user_id))
        ],
    )


async def admins():
    settings = await db.settings.get()
    admin_requests = await db.admin_requests.get()
    buttons = []
    for user_id in settings.bot_admins:
        user_data = admin_requests.get(user_id)
        button_text = f'❌ {user_data.full_name} (@{user_data.username})' if user_data.username else f'❌ {user_data.full_name}'
        buttons.append([InlineButton(button_text, callback_data.AdminRemove(user_id=user_id))])
    if buttons:
        return InlineKeyboard(*buttons)


def user_settings(base_url):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🤖 Параметры нейросети", web_app=WebAppInfo(url=f"{base_url}/settings")
                )
            ]
        ]
    )


def help(base_url):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔌 Подключение бота к группе", web_app=WebAppInfo(url=f"{base_url}/bot_setup")
                )
            ],
            [
                InlineKeyboardButton(
                    text="Почему не GPT-4?", web_app=WebAppInfo(url=f"{base_url}/gpt4")
                )
            ]
        ]
    )
