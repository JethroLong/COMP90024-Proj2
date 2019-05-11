import couchdb

from couchdb import PreconditionFailed
from mpi4py import MPI

import create_views
from process_hashtag import HashtagProcessor
from time_distribution import TimeAnalytics, SentimentTimeAnalytics

url = 'http://127.0.0.1:5984/'
keywords_tweets = 'keyword_tweets'
no_keywords_tweets = 'non_keyword_tweets'

# map functions to be added or edited
ALL_DOC_VIEW_FUNC = "function (doc) {\n emit(doc._id, doc); \n}"
ALL_TEXT_VIEW_FUNC = "function (doc) {\n if (doc.text != null) {\n  emit(doc._id, doc.text);\n }\n}"
HASHTAG_VIEW_FUNC = "function (doc) {\n  if (doc.entities.hashtags.length > 0) {\n     \
                                                emit(doc._id, doc.entities.hashtags);\n  }\n}"

TIME_VIEW_FUNC = "function (doc) {\n  var utc_time = new Date(doc.created_at).getUTCHours();\
                                    \n  emit(doc._id, utc_time); \n}"
DOC_PLACE_VIEW = "function (doc) {\n  if (doc.geo != null) {\n    emit(doc._i d, doc);\n  } \
                        else if (doc.coordinates != null) {\n    emit(doc._id, doc);\n  } \
                        else if (doc.place != null) {\n    emit(doc._id, doc);\n  }\n}"

SENTIMENT_TIME_VIEW = "function (doc) {\n  if (doc.sentiment != null) { \n  \
                        var score = doc.sentiment.compound;\n     \
                        var date = new Date(doc.created_at).getUTCHours();\n   \
                        emit(doc._id, [date, score]);\n  }\n}"

SENTIMENT_DISTRIBUTION_VIEW = "function (doc) {\n  var dict = {};\n  dict['sentiment'] = doc.sentiment.compound;\n  dict['text'] = doc.text;\n  if (doc.coordinates != null){\n    dict['coordinates'] = doc.coordinates;\n    emit(doc._id, dict)\n  }else if (doc.place != null){\n    dict['place'] = doc.place;\n    emit(doc._id, dict)\n  }else if (doc.geo != null){\n    dict['geo'] = doc.geo;\n    emit(doc._id, dict)\n  }\n}"


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    # connect to couch server / tweets dbs
    couch_server = couchdb.Server(url=url)
    keywords_db = couch_server[keywords_tweets]
    no_keywords_db = couch_server[no_keywords_tweets]

    if rank == 0:  # Find trending hashtags
        # create new databases to store processed data
        try:
            hashtag_db = couch_server.create('hashtag')
        except PreconditionFailed:
            hashtag_db = couch_server['hashtag']

        # create views
        view_path = create_views.create_view(url=url, db_name=keywords_tweets, view_name='hashtags',
                                             mapFunc=HASHTAG_VIEW_FUNC,
                                             overwrite=False)
        hashtag_processor = HashtagProcessor(source_db=keywords_db, view_path=view_path, results_db=hashtag_db)
        hashtag_processor.run()
    elif rank == 1:  # what time the keyworded tweets were posted
        # create new databases to store processed data
        try:
            swear_time_db = couch_server.create('time')
        except PreconditionFailed:
            swear_time_db = couch_server['time']

        view_path = create_views.create_view(url=url, db_name=keywords_tweets, view_name='time_distribution',
                                             mapFunc=TIME_VIEW_FUNC,
                                             overwrite=True)
        swear_time_processor = TimeAnalytics(source_db=keywords_db, view_path=view_path, results_db=swear_time_db)
        swear_time_processor.run()
    elif rank == 2:  # sentiment analysis with regard to parts of a day
        # create new databases to store processed data
        try:
            sentiment_db = couch_server.create('time')
        except PreconditionFailed:
            sentiment_db = couch_server['time']
        view_path = create_views.create_view(url=url, db_name=no_keywords_tweets, view_name='sentiment_time',
                                             mapFunc=SENTIMENT_TIME_VIEW,
                                             overwrite=True)
        sentiment_time_processor = SentimentTimeAnalytics(source_db=no_keywords_db, view_path=view_path,
                                                          results_db=sentiment_db)
        sentiment_time_processor.run()
    elif rank == 3:  # sentiment distribution on map
        # create new databases to store processed data
        try:
            sent_place_db = couch_server.create('sentiment')
        except PreconditionFailed:
            sent_place_db = couch_server['sentiment']
        view_path = create_views.create_view(url=url, db_name=no_keywords_tweets, view_name='sentiment_distribution',
                                             mapFunc=SENTIMENT_DISTRIBUTION_VIEW,
                                             overwrite=True)
        sent_area_processor = SentimentTimeAnalytics(source_db=no_keywords_db, view_path=view_path,
                                                     results_db=sent_place_db)
        sent_area_processor.run()


if __name__ == '__main__':
    main()
