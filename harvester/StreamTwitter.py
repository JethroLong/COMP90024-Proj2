import json
import multiprocessing
from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener

# derived from <https://gist.github.com/graydon/11198540>
AUS_BOUND_BOX = (113.338953078, -43.6345972634, 153.569469029, -10.6681857235)


class MyListener (StreamListener):
    """
    In case we want to “keep the connection open”, and gather all
    the upcoming tweets about a particular event, the streaming API
    is what we need. We need to extend the StreamListener() to
    customise the way we process the incoming data.
    """
    def __init__(self, db):
        self.db = db

    def on_data(self, raw_data):
        # record = pre-processing(raw_data)
        # self.db.store(json.loads(record))
        self.db.store(json.loads(raw_data))
        # print(raw_data)

    def on_status(self, status):
        print(status)

    def on_error(self, status_code):
        print("error: ", status_code)


class StreamRunner:
    def __init__(self, db):
        self.db = db

    def run(self, group):
        access_token = group["access_token"]
        access_token_secret = group["access_token_secret"]
        consumer_key = group["consumer_key"]
        consumer_secret = group["consumer_secret"]
        keywords = group["keywords"]

        # Authentication
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        twitter_stream = Stream(auth, MyListener(self.db))
        twitter_stream.filter(track=keywords, locations=AUS_BOUND_BOX, languages=['en'])



