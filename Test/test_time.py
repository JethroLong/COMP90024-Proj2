from collections import Counter

import couchdb

from analytics import create_views
from analytics.time_distribution import SentimentTimeAnalytics
from harvester import Database
import datetime

TIME_VIEW_FUNC = "function (doc) {\n  var utc_time = new Date(doc.created_at).getUTCHours(); \n  emit(doc._id, utc_time); \n}"
SENTIMENT_TIME_VIEW = "function (doc) {\n  if (doc.sentiment != null) { \n  \
                        var score = doc.sentiment.compound;\n     \
                        var date = new Date(doc.created_at).getUTCHours();\n   \
                        emit(doc._id, [date, score]);\n  }\n}"

if __name__ == '__main__':
    url = "http://localhost:5984"
    db_name = "raw_tweets"
    db = Database.DB(url, db_name)
    view_path = create_views.create_view(url=url, db_name=db_name, view_name='sentiment_time', mapFunc=SENTIMENT_TIME_VIEW, overwrite=True)
    view = db.database.view(name=view_path)
    test_db = couchdb.Server(url=url)['test_db']

    # hours = []
    # for each in view:
    #     hours.append(each.value)
    # total_num = len(hours)
    # count = Counter(hours)
    x = SentimentTimeAnalytics(source_db=db.database, view_path=view_path, results_db=test_db)
    sentiment_dict = x.run()
    print(sentiment_dict)
    # for k, v in count.items():
    #     count[k] = float(v/total_num)
    # print(count)