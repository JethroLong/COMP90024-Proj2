import json

import sys
import os

from harvester import StreamTwitter, Database
from harvester.SearchTwitter import Search


def main(argv):
    with open("harvester_config.json", 'r') as template:
        data = json.load(template)
        Groups = data["Groups"]
        new_groups = keyword_distribution(Groups)
        # search_keywords is of length 10, derived from
        # https://listverse.com/2015/09/29/10-offensive-english-words-with-hazy-origins/
        search_keywords = data["search_keywords"]

        # import from system host file
        url = data["db_url"]
        geocode = data["geocode"]

        i = int(argv[2])
        if_key = argv[3]  # -k: streaming using keywords
        if argv[1] == 'stream' and 0 < i <= len(new_groups):
            print("Now start Streaming...")
            if if_key == '-k':
                db_name = 'keyword_tweets'
            else:
                db_name = 'non_keyword_tweets'
            # connect to db
            db = Database.DB(url, db_name)

            stream_mode = StreamTwitter.StreamRunner(db)
            stream_mode.run(new_groups[i-1], if_key)
        elif argv[1] == 'search' and 0 < i <= len(new_groups):
            print("Now start Searching...")
            db_name = 'keyword_tweets'
            # connect to db
            db = Database.DB(url, db_name)

            search_mode = Search(db, geocode)
            search_mode.run(new_groups[i-1], search_keywords)
        else:
            print("Incorrect or lack of Harvesting mode!")


def keyword_distribution(Groups):
    with open("./harvester/offensive_words_corpus.txt", 'r') as corpus:
        indicator = 0
        group_size = len(Groups)
        for keyword in corpus:
            Groups[indicator % group_size]["keywords"].append(keyword[:-1])
            indicator += 1
    return Groups


if __name__ == '__main__':
    # Shell: python3 main.py <mode: stream/search> <token group:1~4> <optional: -k>
    main(sys.argv)

    # for testing
    # main(["", "search", "4"])
