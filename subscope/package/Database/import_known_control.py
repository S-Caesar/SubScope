from subscope.package.Parsing.ichiran import Ichiran
from subscope.package.Database.database import Database


class ImportKnownControl:

    @staticmethod
    def get_deck(path):
        deck = open(path).read().split('\n')
        for idx, entry in enumerate(deck):
            deck[idx] = entry.split('\t')
        return deck

    @staticmethod
    def parse_sentences(sentences, limit=None):
        word_list = []
        for idx, sentence in enumerate(sentences):
            if limit and idx > limit:
                break
            else:
                word_list.extend(Ichiran().convert_line_to_table_rows(sentence, 0))

        words = []
        for entry in word_list:
            words.append(entry[1])
        return words

    @staticmethod
    def mark_known_words(words):
        # Remove duplicates
        words = list(dict.fromkeys(words))
        database = Database().read_database()
        for word in words:
            index = database.loc[database['text'] == word].index
            database.loc[database.index[index], 'status'] = 1
        Database().write_database(database)
