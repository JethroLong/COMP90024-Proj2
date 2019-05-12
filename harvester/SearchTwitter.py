from datetime import datetime
from time import sleep

import tweepy
from tweepy import OAuthHandler

import sentiment


class Search:

    def __init__(self, db, geocode):
        self.geocode = geocode
        self.db = db

    def search_by_keyword(self, para_dict, api):
        # If results only below a specific ID are, set max_id to that ID.
        # else default to no upper limit, start from the most recent tweet matching the search query.
        max_id = -1

        # If results from a specific ID onwards are reqd, set since_id to that ID.
        # else default to no lower limit, go as far back as API allows
        since_id = None if para_dict["since_id"] == -1 else para_dict["since_id"]
        tweets_per_query = 100
        if len(para_dict["keywords"]) > 10:
            query = ' OR '.join(para_dict["keywords"][:10])  # query contains up to 10 keywords
        else:
            query = ' OR '.join(para_dict["keywords"])

        new_tweets = self.do_search(api, query, self.geocode, tweets_per_query, lang='en', since_id=since_id,
                                    max_id=max_id)
        if new_tweets:
            # the most recent id is stored, to be used as the starting point for future
            para_dict["since_id"] = new_tweets[0].id
            for tweet in new_tweets:
                if 'sentiment' not in tweet._json.keys():
                    tweet._json['sentiment'] = sentiment.SentimentAnalyzer.get_scores(tweet._json["text"])
                self.db.store(tweet._json)
            max_id = new_tweets[-1].id  # oldest id was used, as we continue retrieving tweets posted even more earlier

        while True:
            new_tweets = self.do_search(api, query, self.geocode, tweets_per_query, lang='en',
                                        since_id=since_id, max_id=max_id)
            if new_tweets:
                for tweet in new_tweets:
                    if 'sentiment' not in tweet._json.keys():
                        tweet._json['sentiment'] = sentiment.SentimentAnalyzer.get_scores(tweet._json["text"])
                    self.db.store(tweet._json)
                max_id = new_tweets[-1].id

    def do_search(self, api, query, geocode, count=100, lang='en', since_id=None, max_id=-1):
        if max_id <= 0:
            if since_id is None:
                new_tweets = api.search(q=query, count=count, lang=lang, geocode=geocode)
            else:
                new_tweets = api.search(q=query, count=count, since_id=since_id, lang=lang, geocode=geocode)
        else:
            if since_id is None:
                new_tweets = api.search(q=query, count=count, max_id=str(max_id - 1), lang=lang, geocode=geocode)
            else:
                new_tweets = api.search(q=query, count=count, max_id=str(max_id - 1),
                                        since_id=since_id, lang=lang, geocode=geocode)
        return new_tweets

    def setAPI(self, group):
        access_token = group["access_token"]
        access_token_secret = group["access_token_secret"]
        consumer_key = group["consumer_key"]
        consumer_secret = group["consumer_secret"]

        # Authentication
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth)

        return api

    def run(self, group, search_keywords):
        api = self.setAPI(group)
        para_dict = {}
        para_dict["since_id"] = -1
        para_dict["max_id"] = -1
        para_dict["keywords"] = search_keywords
        while True:
            try:
                self.search_by_keyword(para_dict, api)
            except Exception as e:
                until = int(api.last_response.headers['x-rate-limit-reset'])
                until = datetime.fromtimestamp(until)
                delay = (until - datetime.now()).total_seconds()
                print("Rate Limit Reached! Search API not available until {}.".format(until))
                sleep(delay)

            print("All key words searched, loop around after 20 seconds...")
            sleep(20)
            print("para_dict update: ", para_dict)
