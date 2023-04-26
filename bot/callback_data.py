from aiogram.filters.callback_data import CallbackData


class AdminRequestAnswer(CallbackData, prefix='admin_request_answer'):
    decline: bool
    to_user_id: int


class AdminRemove(CallbackData, prefix='admin_remove'):
    user_id: int
