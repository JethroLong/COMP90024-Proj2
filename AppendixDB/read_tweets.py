import json
import couchdb
from harvester import Database

if __name__ == '__main__':
    with open('/Users/jethrolong/Desktop/twitter.json', 'r', encoding='utf-8') as f:
        db = Database.DB(url="http://127.0.0.1:5984", db_name='api_tweets')
        for line in f:
            if not (line.endswith("[\n") or line.endswith("]}\n") or line.endswith("]}")):
                if not (line.endswith("]\n") or line.endswith("]}\n")):
                    if line.endswith("}},\n"):
                        line = line[:-2]
                    else:
                        line = line[:-1]

                    tweet = json.loads(line)['doc']
                    tweet.pop('_rev')
                    try:
                        db.database.save(tweet)
                        print(tweet)
                    except Exception:  # conflict leads to update
                        doc = db.database.get(tweet['_id'])
                        db.database.save(doc)
                        print(doc)
