class HashtagProcessor:

    def __init__(self, source_db, view_path, results_db):
        self.view_path = view_path
        self.source_db = source_db
        self.results_db = results_db

    def run(self):
        view = self.source_db.iterview(name=self.view_path, batch=10000)
        hashtag_occurrence ={}
        for row in view:
            for each in row.value:
                if each['text'].upper() not in hashtag_occurrence.keys():
                    hashtag_occurrence[each['text'].upper()] = 1
                else:
                    hashtag_occurrence[each['text'].upper()] += 1

        record = {"_id": "trending_hashtags", "data": hashtag_occurrence}
        try:
            self.results_db.save(record)
        except Exception:   # conflict leads to update
            doc = self.results_db.get(record['_id'])
            doc['data'] = record['data']
            self.results_db.save(doc)

        print('Hashtag analysis complete ---- results_db/trending_hashtags')
