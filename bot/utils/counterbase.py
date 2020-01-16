# too many rendering bt matplotlib pictures can take too much resources
# and that causes crash, so this module controls that shit

import pymongo


class CounterBase:
    base = {'entity': 'counter'}

    def __init__(self, db_name='TeleWeather', coll_name='Counter'):
        self.client = pymongo.MongoClient()
        self.db = self.client[db_name]
        self.coll = self.db[coll_name]
        self.setup()

    def setup(self):
        if not self.coll.find_one(self.base):
            self.coll.insert({**self.base, 'count': 0})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def get_count(self):
        return self.coll.find_one(self.base)['count']

    def increment(self):
        return self.coll.update_one(self.base, {'$inc': {'count': 1}})

    def decrement(self):
        return self.coll.update_one(self.base, {'$inc': {'count': -1}})
