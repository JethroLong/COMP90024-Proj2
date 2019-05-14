from text_tokenizer import TextProcessor


class SentimentPlaceAnalytics:

    def __init__(self, source_db, view_path, results_db):
        self.view_path = view_path
        self.source_db = source_db
        self.results_db = results_db

    def plot(self):
        pass

    def run(self):
        print('Sentiment Place distribution analysis Start...')
        sentiment_cor_list = []
        for iter in range(50):
            view = self.source_db.view(name=self.view_path, limit=10000, skip=iter*10000)
            # view = self.source_db.view(name=self.view_path, limit=10000)
            count = 0
            for each in view:
                temp_dict = {}
                if 'coordinates' in each.value.keys():
                    temp_dict['coordinates'] = each.value['coordinates']['coordinates']
                    temp_dict['sentiment'] = each.value['sentiment']
                    temp_dict['text'] = TextProcessor.remove_pattern(each.value['text'])
                    sentiment_cor_list.append(temp_dict)
                    count += 1
                if count == 100:
                    break

        record = {'_id': "sentiment_distribution", "data": sentiment_cor_list}

        try:
            self.results_db.save(record)
        except Exception:  # conflict leads to update
            doc = self.results_db.get(record['_id'])
            doc['data'] = record['data']
            self.results_db.save(doc)

        print('Sentiment Place distribution analysis complete ---- results_db/sentiment_distribution')




