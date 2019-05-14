import sys

sys.path.append("/mnt/storage/COMP90024-Proj2-master")
sys.path.append("/Users/jethrolong/pyCharmProjects/COMP90024-Proj2")

import couchdb
from harvester import read_host
import json
import create_views

from couchdb import PreconditionFailed
from process_hashtag import HashtagProcessor
from time_distribution import TimeAnalytics, SentimentTimeAnalytics
from sentiment_distribution import SentimentPlaceAnalytics


keywords_tweets = 'keyword_tweets'
no_keywords_tweets = 'non_keywords'

# map functions to be added or edited
ALL_DOC_VIEW_FUNC = "function (doc) {\n emit(doc._id, doc); \n}"
HAS_GEO_VIEW_FUNC = "function (doc) {\n  if (doc.coordinates != null){\n    var x = {};\n    x['coordinates'] =  doc.coordinates.coordinates;\n    x['text'] = doc.text;\n    emit(doc._id, x);\n  }\n}"

HASHTAG_VIEW_FUNC = "function (doc) {\n  if (doc.entities.hashtags.length > 0) {\n emit(doc._id, doc.entities.hashtags);\n  }\n}"

TIME_VIEW_FUNC = "function (doc) {\n  var utc_time = new Date(doc.created_at).getUTCHours();\n  emit(doc._id, utc_time); \n}"

SENTIMENT_TIME_VIEW = "function (doc) {\n  if (doc.sentiment != null) { \n var score = doc.sentiment.compound;\n var date = new Date(doc.created_at).getUTCHours();\n emit(doc._id, [date, score]);\n  }\n}"

SENTIMENT_DISTRIBUTION_VIEW = "function (doc) {\n  var dict = {};\n  dict['sentiment'] = doc.sentiment.compound;\n  dict['text'] = doc.text;\n  if (doc.coordinates != null){\n    dict['coordinates'] = doc.coordinates;\n    emit(doc._id, dict)\n  }\n}"


def get_db_url():
    couchdb_ip = read_host.ReadHost.read()
    print("db url={}".format(couchdb_ip))
    couchdb_port = str(5984)
    url = "http://{}:{}".format(couchdb_ip, couchdb_port)
    # url = "http://172.26.38.109:5984"
    return url


def main(overwrite=False):
    url = get_db_url()

    # connect to couch server / tweets dbs
    couch_server = couchdb.Server(url=url)
    keywords_db = couch_server[keywords_tweets]
    no_keywords_db = couch_server[no_keywords_tweets]

    # create new databases to store processed data
    try:
        results_db = couch_server.create('test')  # results
    except PreconditionFailed:
        results_db = couch_server['test']

    # Find trending hashtags
    # create views
    view_path = create_views.create_view(url=url, db_name=keywords_tweets, view_name='hashtags',
                                         mapFunc=HASHTAG_VIEW_FUNC,
                                         overwrite=overwrite)
    hashtag_processor = HashtagProcessor(source_db=keywords_db, view_path=view_path, results_db=results_db)
    hashtag_processor.run()

    # what time the keyworded tweets were posted
    # create view
    view_path = create_views.create_view(url=url, db_name=keywords_tweets, view_name='time_distribution',
                                         mapFunc=TIME_VIEW_FUNC,
                                         overwrite=overwrite)
    swear_time_processor = TimeAnalytics(source_db=keywords_db, view_path=view_path, results_db=results_db)
    swear_time_processor.run()

    # sentiment analysis with regard to parts of a day
    view_path = create_views.create_view(url=url, db_name=no_keywords_tweets, view_name='sentiment_time',
                                         mapFunc=SENTIMENT_TIME_VIEW,
                                         overwrite=overwrite)
    sentiment_time_processor = SentimentTimeAnalytics(source_db=no_keywords_db, view_path=view_path,
                                                      results_db=results_db)
    sentiment_time_processor.run()

    # sentiment distribution on map
    view_path = create_views.create_view(url=url, db_name=no_keywords_tweets, view_name='sentiment_distribution',
                                         mapFunc=SENTIMENT_DISTRIBUTION_VIEW,
                                         overwrite=overwrite)
    sent_area_processor = SentimentPlaceAnalytics(source_db=no_keywords_db, view_path=view_path,
                                                  results_db=results_db)
    sent_area_processor.run()

    # correlation
    # view_path = create_views.create_view(url=url, db_name=no_keywords_tweets, view_name='sentiment_distribution',
    #                                      mapFunc=SENTIMENT_DISTRIBUTION_VIEW,
    #                                      overwrite=False)
    # sent_area_processor = SentimentPlaceAnalytics(source_db=no_keywords_db, view_path=view_path,
    #                                               results_db=results_db)
    # sent_area_processor.run()


if __name__ == '__main__':
    overwrite = sys.argv[1] if len(sys.argv) > 1 else False
    main(overwrite)
