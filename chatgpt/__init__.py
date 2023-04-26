import json
import logging

import aiohttp
from aiohttp import ClientSession


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
            print(r.status)
            if r.status == 200:
                return await r.json()

    async def get_models(self):
        return await self.get('/v1/models')

    async def completions(self, messages: list[dict], temperature=1.0):
        response = await self.post('/v1/chat/completions', model=self.default_model, messages=messages,
                                   temperature=temperature)
        return response['choices'][0]['message']['content']
