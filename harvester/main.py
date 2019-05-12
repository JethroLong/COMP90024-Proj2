import json
import readhost
import sys
import os

import Database, StreamTwitter
from SearchTwitter import Search


def main(argv):
    with open("./harvester_config.json", 'r') as template:
        data = json.load(template)
        Groups = data["Groups"]
        new_groups = keyword_distribution(Groups)
        # search_keywords is of length 10, derived from
        # https://listverse.com/2015/09/29/10-offensive-english-words-with-hazy-origins/
        search_keywords = data["search_keywords"]

        # import from system host file
        #url = data["db_url"]
        couchdb_ip = json.loads(readhost.read())["couchdb"]
        couchdb_port = str(5984)
        url_str = 'http://' + couchdb_ip + ':' + couchdb_port
        url = data["url_str"]
        
        geocode = data["geocode"]

        i = int(argv[2])
        if_key = argv[3]  # -k: streaming using keywords
        if argv[1] == 'stream' and 0 < i <= len(new_groups):
            if if_key == '-k':
                db_name = 'keyword_tweets'
                print("Now start keyword Streaming...")
            elif if_key == '-K':  # -K: streaming without keywords
                print("Now start non-keyword Streaming...")
                db_name = 'non_keyword_tweets'
            else:
                print('Optional command Error')
                sys.exit(0)

            # connect to db
            db = Database.DB(url, db_name)
            stream_mode = StreamTwitter.StreamRunner(db)
            stream_mode.run(i, new_groups[i-1], if_key)
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
    with open("./offensive_words_corpus.txt", 'r') as corpus:
        indicator = 0
        group_size = len(Groups)
        for keyword in corpus:
            Groups[indicator % group_size]["keywords"].append(keyword[:-1])
            indicator += 1
    return Groups


if __name__ == '__main__':
    # Shell: python3 main.py <mode: stream/search> <token group:1~4> <optional: -k / -K>

    main(sys.argv)

    # for testing
    # main(["", "search", "4"])
