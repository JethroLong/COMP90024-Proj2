from nltk.corpus import wordnet
file_name_list = ['bad-words.txt',
                  'body_parts_mild.txt', 'body_parts_medium.txt', 'body_parts_strong.txt', 'body_parts_strongest.txt',
                  'gender_identity_mild.txt', 'gender_identity_medium.txt',
                  'gender_identity_strong.txt', 'gender_identity_strongest.txt',
                  'mental_health_physical_disability_mild.txt', 'mental_health_physical_disability_medium.txt',
                  'mental_health_physical_disability_strong.txt', 'mental_health_physical_disability_strongest.txt',
                  'race_ethnicity_mild.txt', 'race_ethnicity_medium.txt',
                  'race_ethnicity_strong.txt', 'race_ethnicity_strongest.txt',
                  'sexual_reference_mild.txt', 'sexual_reference_medium.txt', 'sexual_reference_strong.txt',
                  'older_people_mild.txt', 'older_people_medium.txt',
                  'religious_insults_strong.txt',
                  ]
MOST_COMM_TIMES = 5
WORD_FREQ_THRESHOLD = 20

def has_primary_sense(word):
    # filter words without primary sense
    if len(wordnet.synsets(word)) > 0:
        if len(wordnet.synsets(word)) != 1:  # words with multiple sense
            most_comm = 0
            second_comm = 0
            # count the most and second common sense
            for synset in wordnet.synsets(word):
                for i in range(len(synset.lemma_names())):
                    if synset.lemma_names()[i].lower() == word:
                        ass_lemma = synset.lemmas()[i]
                        if ass_lemma.count() > most_comm:
                            most_comm = ass_lemma.count()
                        elif ass_lemma.count() > second_comm:
                            second_comm = ass_lemma.count()

            if most_comm >= MOST_COMM_TIMES * second_comm and most_comm > 0:
                return True

        else:  # words with single sense
            return True

    else:  # words not in wordnet synset
        return True

    return False


def is_common_word(word):
    synsets = wordnet.synsets(word)
    freq = 0
    for s in synsets:
        for lemm in s.lemmas():
            freq += lemm.count()
    # if freq > 0:
        # print(word, ": ", freq)
    return freq


def doc_tokenize():
    pass


def word_lemmatize(doc, nlp):
    doc = nlp(doc)
    for word in doc:
        return word.lemma_


def main():
    corpus = set()
    for file_name in file_name_list:  # combine two corpus
        file = open(file_name, 'r+')
        sub_corpus = set()
        for word in file:
            word = word.replace('\n', '')
            freq = is_common_word(word)
            if not (freq >= WORD_FREQ_THRESHOLD and not has_primary_sense(word)):  # remove frequent and ambiguous words
                word = word.lower()  # lowercase
                if '-' in word:
                    sub_corpus.add(word.replace('-', ' '))
                else:
                    sub_corpus.add(word)
            else:
                print(word, " invalid")
        corpus = corpus.union(sub_corpus)
        file.truncate(0)
        file.seek(0)  # overwrite preprocessed words into catalogued corpus
        print(sub_corpus)
        for word in sub_corpus:
            file.writelines(word+'\n')
        file.close()

        new_file = open("offensive_words_corpus.txt", "w+")
        for word in corpus:
            new_file.writelines(word)
        new_file.close()


if __name__ == '__main__':
    main()
