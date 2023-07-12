import json
import logging
from typing import Any

import aiohttp
from aiohttp import ClientSession


def parse_context_messages(messages: list[dict | object]) -> list[dict[str, Any]]:
    """
    Преобразует список сообщений в список словарей, содержащих только атрибуты 'content' и 'role'.

    :param messages: Список сообщений, которые могут быть представлены как словари или объекты с атрибутами 'content' и 'role'.
    :type messages: list[dict | object]

    :return: Список словарей, содержащих только атрибуты 'content' и 'role'.
    :rtype: list[dict[str, Any]]
    """
    parsed_messages = [
        dict(content=message['content'], role=message['role'])
        if isinstance(message, dict)
        else dict(content=message.content, role=message.role)
        for message in messages
    ]

    return parsed_messages


class ChatGPT:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        self.endpoint = 'https://api.openai.com'
        self.default_model = 'gpt-3.5-turbo'

        self.session: ClientSession

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        logging.info('ChatGPT - Создана сессия.')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logging.info('ChatGPT - Закрываю сессию...')
        await self.session.close()
        logging.info('ChatGPT - Сессия закрыта.')

    async def get(self, path, **params):
        kwargs = {'headers': self.headers}
        if params:
            kwargs['data'] = json.dumps(params)

        async with self.session.get(self.endpoint + path, **kwargs) as r:
            print(r.status)
            if r.status == 200:
                return (await r.json()).get('data')

    async def post(self, path, **params):
        kwargs = {'headers': self.headers}
        if params:
            kwargs['data'] = json.dumps(params)

        async with self.session.post(self.endpoint + path, **kwargs) as r:
            return await r.json()

    async def get_models(self):
        return await self.get('/v1/models')

    async def completions(self, messages: list[dict | object],
                          max_tokens=None,
                          n=None,
                          stop=None,
                          temperature=1.0,
                          top_p=1.0,
                          presence_penalty=0.0,
                          frequency_penalty=0.0):
        """
        https://beta.openai.com/docs/api-reference/chat/create
        :param messages: класс или словарь, где должны быть атрибуты/ключи 'content' и 'role'
        :param max_tokens: The maximum number of tokens(common sequences of characters found in text) to generate in the completion.
        :param n: How many completions to generate for each prompt.
        :param stop: Up to 4 sequences where the API will stop generating further tokens.
        :param temperature: What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer.
        :param top_p: An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
        :param presence_penalty: What penalty to apply when a token is already present at all in the text.
        :param frequency_penalty: What penalty to apply when a token has been generated recently.
        """
        response = await self.post('/v1/chat/completions', model=self.default_model,
                                   messages=parse_context_messages(messages),
                                   max_tokens=max_tokens,
                                   n=n,
                                   stop=stop,
                                   temperature=float(temperature),
                                   top_p=float(top_p),
                                   presence_penalty=float(presence_penalty),
                                   frequency_penalty=float(frequency_penalty))
        return response
