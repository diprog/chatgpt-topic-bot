from db import pickler, database


class BaseModel:
    def __init__(self, id, collection: str):
        self.id = id
        self.collection = collection

    async def save(self):
        try:
            self.__delattr__('_id')
        except AttributeError:
            pass

        find_query = {'id': self.id}

        obj_dict = pickler.flatten(self)
        del obj_dict['collection']

        set_query = {'$set': obj_dict}

        await database[self.collection].update_one(find_query, set_query, upsert=True)

    @staticmethod
    async def get(collection, **query):
        if document := await database[collection].find_one(query):
            obj = pickler.restore(document)
            obj.collection = collection
            return obj
        else:
            print('not found')
