import re

regex_str = [
    r'<[^>]+>',  # HTML tags
    r'(?:@[\w_]+)',  # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+'  # URLs
]


class TextProcessor:

    @staticmethod
    def remove_pattern(text):
        return re.sub(r'(' + '|'.join(regex_str) + ')',  repl='', string=text)
