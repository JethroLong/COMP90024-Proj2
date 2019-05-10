import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


class SentimentAnalyzer:

    @staticmethod
    def get_scores(sentence):
        try:
            analyzer = SentimentIntensityAnalyzer()
            temp_scores = analyzer.polarity_scores(sentence)
            return temp_scores
        except Exception as e:
            nltk.download('vader_lexicon')
            return analyzer.polarity_scores(sentence)



    @staticmethod
    def count_sentiment(self, temp_scores):
        pass