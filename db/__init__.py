from copy import copy

import aiofiles
import jsonpickle

cache = {}


class DataFile:
    def __init__(self, filename: str):
        self.path = f'db/data/{filename}.json'

    def save_to_cache(self, obj):
        global cache
        cache[self.path] = obj

    def read_from_cache(self):
        global cache
        try:
            return copy(cache[self.path])
        except KeyError:
            return None

    async def read(self):
        global cache

        if obj := self.read_from_cache():
            return obj

        try:
            async with aiofiles.open(self.path, 'r', encoding='utf-8') as f:
                self.save_to_cache(jsonpickle.decode(await f.read(), keys=True))
                return self.read_from_cache()
        except FileNotFoundError:
            return None

    async def write(self, obj):
        async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:
            self.save_to_cache(obj)
            await f.write(jsonpickle.encode(obj, keys=True))


def delete_cache(path):
    try:
        del cache[path]
    except KeyError:
        pass
