import json
import logging

import aiohttp
from aiohttp import ClientSession


def parse_context_messages(messages: list[dict | object]):
    parsed_messages = []
    for message in messages:
        if type(message) is dict:
            parsed_messages.append(dict(content=message['content'], role=message['role']))
        else:
            parsed_messages.append(dict(content=message.content, role=message.role))
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
            if r.status == 200:
                return await r.json()
            logging.info(r.status)
            logging.info(await r.text())

    async def get_models(self):
        return await self.get('/v1/models')

    async def completions(self, messages: list[dict | object],
                          max_tokens=None,
                          n=None,
                          stop=None,
                          temperature=1.0,
                          frequency_penalty=0.0,
                          presence_penalty=0.0,
                          best_of=None,
                          logprobs=None):
        """
        https://beta.openai.com/docs/api-reference/completions/create
        :param messages: класс или словарь, где должны быть атрибуты/ключи 'content' и 'role'
        :param max_tokens: The maximum number of tokens(common sequences of characters found in text) to generate in the completion.
        :param n: How many completions to generate for each prompt.
        :param stop: Up to 4 sequences where the API will stop generating further tokens.
        :param temperature: What sampling temperature to use. Higher values means the model will take more risks.
        :param frequency_penalty: What sampling penalty to apply based on token frequency. High values will bias towards repeating the same overused tokens.
        :param presence_penalty: What sampling penalty to apply based on token presence in the text so far. High values will bias against tokens that already appear in the text.
        :param best_of: Generates best_of completions server-side and returns the "best" (as evaluated by the model) completion(s).
        :param logprobs: Include a log probability on the likelihood of each completion token using this parameter value as a cutoff threshold.

        """

        response = await self.post('/v1/completions', model=self.default_model,
                                   prompt=parse_context_messages(messages),
                                   max_tokens=max_tokens,
                                   n=n,
                                   stop=stop,
                                   temperature=temperature,
                                   frequency_penalty=frequency_penalty,
                                   presence_penalty=presence_penalty,
                                   best_of=best_of,
                                   logprobs=logprobs)

        return response['choices'][0]['text']
