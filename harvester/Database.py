import multiprocessing
import json
import couchdb
from couchdb import PreconditionFailed


class DB:

    def __init__(self, url, db_name):
        self.server = couchdb.Server(url)  # connect to db
        self.lock = multiprocessing.Lock()
        try:
            self.database = self.server.create(db_name)
        except PreconditionFailed:
            self.database = self.server[db_name]

    def store(self, data):
        self.lock.acquire()
        if isinstance(data, dict):
            temp_tweet = data
        else:
            temp_tweet = json.loads(data)
        try:
            record = self.database.get(temp_tweet["id_str"])
            if record is None:  # check if db already has a copy, using id_str
                temp_tweet["_id"] = temp_tweet["id_str"]  # set the primary key
                self.database.save(temp_tweet)
            else:
                pass
        except Exception as e:
            pass
        self.lock.release()
