from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from bot import router


@router.message(Command(commands=["webview"]))
async def command_webview(message: Message, base_url: str):
    await message.answer(
        "Test",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Open Webview", web_app=WebAppInfo(url=f"{base_url}/settings")
                    )
                ]
            ]
        ),
    )
