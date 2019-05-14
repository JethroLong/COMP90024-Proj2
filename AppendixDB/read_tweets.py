import json
import time

import couchdb
from mpi4py import MPI
from harvester import Database
from harvester.sentiment import SentimentAnalyzer

db = Database.DB(url="http://10.13.38.163:5984", db_name='keyword_tweets')


def saveTweets(line_record, processor, add, up, cnt):
    tweet = json.loads(line_record)['doc']
    if 'text' in tweet.keys():
        tweet.pop('_rev')
        tweet['sentiment'] = SentimentAnalyzer.get_scores(tweet['text'])

        try:
            db.database.save(tweet)
            add += 1
            cnt += 1
        except Exception:  # conflict leads to update
            doc = db.database.get(tweet['_id'])
            doc['sentiment'] = SentimentAnalyzer.get_scores(tweet['text'])
            db.database.save(doc)
            up += 1
            cnt += 1

        if count % 1000 == 0:
            print("Process{}:  Processed: {},  New tweets: {}, Updates: {}".format(processor, count, new_add, update))

        return add, up, cnt


if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    time_start = time.time()
    with open('/Users/jethrolong/Desktop/keyword_tweets', 'r', encoding='utf-8') as f:
        count = 0
        new_add = 0
        update = 0
        row_indicator = 0
        for line in f:
            if not (line.endswith("[\n") or line.endswith("]}\n") or line.endswith("]}")):
                if not (line.endswith("]\n") or line.endswith("]}\n")):
                    row_indicator += 1

                    if rank == (row_indicator % size):
                        if line.endswith("}},\n"):
                            line = line[:-2]
                        else:
                            line = line[:-1]
                        new_add, update, count = saveTweets(line, rank, new_add, update, count)

        comm.barrier()
        time_end = time.time()

        # gather information from other processes
        new_add = comm.gather(new_add, root=0)
        update = comm.gather(update, root=0)
        count = comm.gather(count, root=0)

        time_diff = comm.gather((time_end - time_start), root=0)
        if rank == 0:
            count = sum(count)
            new_add = sum(new_add)
            update = sum(update)
            print("Total num of docs:{}, New tweets: {}, Updates:{} ".format(count, new_add, update))
            print("Total time used (average): %.3f sec." % (sum(time_diff) / len(time_diff)) + "\n")

