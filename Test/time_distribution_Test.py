import couchdb

from analytics import create_views
from analytics.time_distribution import TimeAnalytics

TIME_VIEW_FUNC = "function (doc) {\n  var utc_time = new Date(doc.created_at).getUTCHours();\
                                    \n  emit(doc._id, utc_time); \n}"

if __name__ == '__main__':
    url = "http://10.9.131.221:5984"
    db_name = 'raw_tweets'
    server = couchdb.Server(url)
    db = server[db_name]
    results_db = server['test_db']


    view_path = create_views.create_view(url=url, db_name=db_name, view_name='time_distribution',
                                         mapFunc=TIME_VIEW_FUNC,
                                         overwrite=True)
    swear_time_processor = TimeAnalytics(source_db=db, view_path=view_path, results_db=results_db)
    swear_time_processor.run()