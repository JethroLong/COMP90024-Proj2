import json
import couchdb
from harvester import Database
from harvester.sentiment import SentimentAnalyzer

if __name__ == '__main__':
    with open('/Users/jethrolong/Desktop/twitter.json', 'r', encoding='utf-8') as f:
        db = Database.DB(url="http://172.26.38.109:5984", db_name='non_keyword_tweets')
        count = 0
        new_add = 0
        update = 0
        for line in f:
            if not (line.endswith("[\n") or line.endswith("]}\n") or line.endswith("]}")):
                if not (line.endswith("]\n") or line.endswith("]}\n")):
                    if line.endswith("}},\n"):
                        line = line[:-2]
                    else:
                        line = line[:-1]

                    tweet = json.loads(line)['doc']
                    tweet.pop('_rev')
                    tweet['sentiment'] = SentimentAnalyzer.get_scores(tweet['text'])

                    try:
                        db.database.save(tweet)
                        new_add += 1
                        count += 1
                    except Exception:  # conflict leads to update
                        doc = db.database.get(tweet['_id'])
                        doc['sentiment'] = SentimentAnalyzer.get_scores(tweet['text'])
                        db.database.save(doc)
                        update += 1
                        count += 1
            if count % 1000 == 0:
                print("Processed: {},  New tweets: {}, Updates: {}".format(count, new_add, update))
        print("Total num of docs: ", count)