import json
from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener
import sentiment
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
        try:
            tweet = json.loads(raw_data)
            if 'sentiment' not in tweet.keys():
                tweet['sentiment'] = sentiment.SentimentAnalyzer.get_scores(tweet["text"])
            self.db.store(tweet)
        except Exception:
            pass

    def on_status(self, status):
        print(status)

    def on_error(self, status_code):
        print("error: ", status_code)


class StreamRunner:
    def __init__(self, db):
        self.db = db

    def run(self, i, group, if_key):
        access_token = group["access_token"]
        access_token_secret = group["access_token_secret"]
        consumer_key = group["consumer_key"]
        consumer_secret = group["consumer_secret"]
        keywords = group["keywords"]

        # Authentication
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        twitter_stream = Stream(auth, MyListener(self.db))

        try:
            if if_key == '-k':
                twitter_stream.filter(track=keywords, locations=AUS_BOUND_BOX, languages=['en'])
            elif if_key == '-K':
                twitter_stream.filter(locations=AUS_BOUND_BOX, languages=['en'])
        except Exception:
            print("Group {} Stream Disconnected".format(i))
            self.run(i, group, if_key)




