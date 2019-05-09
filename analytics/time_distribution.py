from collections import Counter


class TimeAnalytics:

    def __init__(self, source_db, view_path, results_db):
        self.view_path = view_path
        self.source_db = source_db
        self.results_db = results_db

    def plot(self, hour_freq_dict):
        pass

    def run(self):
        view = self.source_db.iterview(name=self.view_path, batch=10000)
        hours = []
        for each in view:
            hours.append(each.value)
        total_num = len(hours)
        hour_freq_dict = Counter(hours)
        for k, v in hour_freq_dict.items():
            hour_freq_dict[k] = float(v/total_num)

        record = {"_id": "tweet_time", "date": hour_freq_dict}
        self.results_db.save(record)

class SentimentTimeAnalytics:

    def __init__(self, source_db, view_path, results_db):
        self.view_path = view_path
        self.source_db = source_db
        self.results_db = results_db

    def plot(self):
        pass

    def sentiment_classifier(self, compound):
        if compound >= 0.05:
            return 'pos'
        elif -0.05 < compound < 0.05:
            return 'neu'
        elif compound <= -0.05:
            return 'neg'

    def run(self):
        view = self.source_db.iterview(name=self.view_path, batch=10000)
        sentiment_dict = {"morning": {}, "afternoon": {}, "evening": {}, "night": {}}
        for each in view:
            if 5 <= each.value[0] <= 11:  # morning 5.00 ~ 11.59
                sentiment = self.sentiment_classifier(each.value[1])
                if sentiment in sentiment_dict['morning'].keys():
                    sentiment_dict['morning'][sentiment] += 1
                else:
                    sentiment_dict['morning'][sentiment] = 1
            elif 12 <= each.value[0] <= 16:  # afternoon 12.00 ~ 16.59
                sentiment = self.sentiment_classifier(each.value[1])
                if sentiment in sentiment_dict['afternoon'].keys():
                    sentiment_dict['afternoon'][sentiment] += 1
                else:
                    sentiment_dict['afternoon'][sentiment] = 1
            elif 17 <= each.value[0] <= 20:  # evening 17.00 ~ 20.59
                sentiment = self.sentiment_classifier(each.value[1])
                if sentiment in sentiment_dict['evening'].keys():
                    sentiment_dict['evening'][sentiment] += 1
                else:
                    sentiment_dict['evening'][sentiment] = 1
            elif 21 <= each.value[0] <= 23 or 0 <= each.value[0] <= 4:
                sentiment = self.sentiment_classifier(each.value[1])
                if sentiment in sentiment_dict['night'].keys():
                    sentiment_dict['night'][sentiment] += 1
                else:
                    sentiment_dict['night'][sentiment] = 1

        record = {"_id": "sentiment_time", 'data':sentiment_dict}
        self.results_db.save(record)
