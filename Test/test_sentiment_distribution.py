import pickle

import couchdb

from analytics import create_views
from harvester import Database
import matplotlib.pyplot as plt
import matplotlib


SENTIMENT_DISTRIBUTION_VIEW = "function (doc) {\n  var dict = {};\n  var sentiment = doc.sentiment.compound;\n  dict['sentiment'] = sentiment;\n  if (doc.coordinates != null){\n    dict['coordinates'] = doc.coordinates;\n    emit(doc._id, dict)\n  }else if (doc.place != null){\n    dict['place'] = doc.place;\n    emit(doc._id, dict)\n  }else if (doc.geo != null){\n    dict['geo'] = doc.geo;\n    emit(doc._id, dict)\n  }\n}"


if __name__ == '__main__':
    url = "http://localhost:5984"
    db_name = "raw_tweets"
    db = Database.DB(url, db_name)
    view_path = create_views.create_view(url=url, db_name=db_name, view_name='sentiment_distribution', mapFunc=SENTIMENT_DISTRIBUTION_VIEW, overwrite=False)
    view = db.database.iterview(name=view_path, batch=10000)

    sentiment_cor_list = []
    count = 0
    for each in view:
        count += 1
        temp_dict = {}
        if 'coordinates' in each.value.keys():
            temp_dict['coordinates'] = each.value['coordinates']['coordinates']
            temp_dict['sentiment'] = each.value['sentiment']
            sentiment_cor_list.append(temp_dict)
        elif 'geo' in each.value.keys():
            temp_dict['coordinates'] = each.value['geo']['coordinates'][::-1]
            temp_dict['sentiment'] = each.value['sentiment']
            sentiment_cor_list.append(temp_dict)
        elif 'place' in each.value.keys():
            if 'coordinates' in each.value['place']['bounding_box'].keys():
                x_list = [x[0] for x in each.value['place']['bounding_box']['coordinates'][0]]
                y_list = [x[1] for x in each.value['place']['bounding_box']['coordinates'][0]]
                # print("x: ", x_list, "      y: ", y_list)
                temp_dict['coordinates'] = [sum(x_list) / float(len(x_list)), sum(y_list) / float(len(y_list))]
                temp_dict['sentiment'] = each.value['sentiment']
                sentiment_cor_list.append(temp_dict)

    results_db = couchdb.Server(url=url)['test_db']

    record = {'_id': "sentiment_distribution", "data": sentiment_cor_list}
    results_db.save(record)
    fig = plt.figure()
    for each in sentiment_cor_list:
        plt.plot(each['coordinates'])
    plt.show()
    server = couchdb.Server(url=url)
    test_db = server['test_db']
    fig.savefig('test_fig.png')
    # f = open('test_fig.png', 'r', encoding='utf-8')
    # new_record = {"fig_data": sentiment_cor_list}
    # # new_record['_id'] = "1"
    # # test_db.save(new_record)
    # # test_db.put_attachment(doc=new_record, content=f, filename='figure.png', content_type='image/png')
    # f.close()