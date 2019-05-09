from collections import Counter

import couchdb
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import vincent
from vincent import AxisProperties, PropertySet, ValueRef

from analytics import create_views
from harvester import Database

ALL_DOC_VIEW_FUNC = "function (doc) {\n emit(doc._id, doc); \n}"
HAS_GEO_VIEW_FUNC = "function (doc) {\n  if (doc.geo != null) {\n     emit(doc._id, doc.geo);\n  }\n}"
VALID_DOC_VIEW = "function (doc) {\n  if (doc.geo != null) {\n    emit(doc._id, doc);\n  } \
                        else if (doc.coordinates != null) {\n    emit(doc._id, doc);\n  } \
                        else if (doc.place != null) {\n    emit(doc._id, doc);\n  }\n}"
HASHTAG_VIEW_FUNC = "function (doc) {\n  if (doc.entities.hashtags.length > 0) {\n     emit(doc._id, doc.entities.hashtags);\n  }\n}"


if __name__ == '__main__':
    url = "http://localhost:5984"
    db_name = "raw_tweets"
    db = Database.DB(url, db_name)
    view_path = create_views.create_view(url=url,db_name=db_name, view_name='hashtags',mapFunc=HASHTAG_VIEW_FUNC, overwrite=True)
    view = db.database.view(name=view_path)
    count = 1
    hashtag_occurrence = {}
    for row in view:
        for each in row.value:
            if each['text'].upper() not in hashtag_occurrence.keys():
                hashtag_occurrence[each['text'].upper()] = 1
            else:
                hashtag_occurrence[each['text'].upper()] += 1
    results_db = Database.DB(url, 'test_db')
    record = {"_id": "trending_hashtags", "data": hashtag_occurrence}
    results_db.database.save(record)
    # hashtag_occurrence = sorted(hashtag_occurrence.items(), reverse=True, key=lambda x: x[-1])
    #
    # couch = couchdb.Server(url=url)
    # try:
    #     test_hashtag = couch.create('test_hashtag')
    # except:
    #     test_hashtag = couch['test_hashtag']
    #
    # record = {"ordered_hashtags": hashtag_occurrence}

    count_terms_only = Counter()
    count_terms_only.update(hashtag_occurrence)
    top10 = count_terms_only.most_common(10)
    hashtag, occurrences = zip(*top10)
    # axes = figure.add_axes()
    # data = {'y': occurrences, 'x': hashtag}
    # # plt.bar(range(len(top10)), top10)
    # bar_chart = vincent.Bar(data, iter_idx='x')
    # bar_chart.axis_titles(x='Hashtags', y='Occurrences',)
    # rotate_x = AxisProperties(labels=PropertySet(angle=ValueRef(value=45), align=ValueRef(value='left')))
    # bar_chart.axes[0].properties = rotate_x
    # bar_chart.to_json('sample.json')
    # print(bar_chart.grammar)
    # test_hashtag.save(record)
    # print(hashtag_occurrence)


        # sentiment = SentimentAnalyzer.get_scores(each.value)
        # print(sentiment)
    # print(SentimentAnalyzer.get_scores())
    # text = "RT @WByng: U.N. human rights office on Wednesday condemned the beheadings of 37 Saudi minority Shi’ite Muslims, following false confessions… @ReclaimAnglesea Wonderful news 😊 "
    # print(text_tokenizer.tokenize())
    # print(SentimentAnalyzer.get_scores(text_tokenizer.tokenize(text)))
    # print(SentimentAnalyzer.get_scores(text))

    # path = create_views.create_view(url=url, db_name=db_name, view_name="all_view", mapFunc=ALL_DOC_VIEW_FUNC, recreate=True)
    # print(path)
