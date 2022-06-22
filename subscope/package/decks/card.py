import random
import datetime
from enum import Enum

from subscope.package.database.database import Database
from subscope.package.utilities.media_use_case import MediaUseCase


class CardHeading(Enum):
    REVIEW_STATE = 'Review State'
    SOURCE = 'Source'
    ANALYSED_OUTPUT = 'Analysed Output'
    LINE_NUMBER = 'Line Number'
    WORD = 'Word'
    GLOSS = 'Gloss'
    SENTENCE = 'Sentence'
    AUDIO_CLIP = 'Audio Clip'
    SCREENSHOT = 'Screenshot'
    SCORE = 'Score'
    LAST_REVIEW = 'Last Review'
    NEXT_REVIEW = 'Next Review'
    STATUS = 'Status'

    def __init__(self, text):
        self.text = text


class Card:
    # TODO: I'll probably need to use a Builder so I can create cards either from a word, or a Deck entry
    def __init__(self, word=None, deck_entry=None):
        self.word = word
        self._deck_entry = deck_entry
        if word is not None:
            self._create_from_word()
        else:
            self._create_from_deck_entry()

    def entry(self):
        # TODO: At the moment, these don't tie in with the CardHeading names, so both need to be changed together
        entry = [self._review_state, self._source, self._episode, self._line_number, self.word, self._gloss,
                 self._sentence, self.audio_clip_path, self.screenshot_path, self._score, self._last_review,
                 self._next_review, self._status]
        return entry

    def _create_from_word(self):
        database = Database.read_database()
        word_entry = database[database['reading'] == self.word].reset_index(drop=True)
        data_columns = Database.get_words_data_headers()

        index = word_entry.columns.get_loc(data_columns[-1]) + 1
        sources = word_entry.iloc[:, index:]
        sources_containing_word = list(sources.loc[:, (sources >= 1).any()].columns)
        selected_source = random.choice(sources_containing_word).split('/')
        word_data = dict(zip(word_entry.columns, list(word_entry.iloc[0])))

        self._review_state = 0
        self._score = 2.5
        self._source = selected_source[0]
        self._episode = selected_source[1]
        self._line_number = Database.word_line_number(self.word, self._source, self._episode)
        self._gloss = word_data['gloss']
        self._sentence = Database.sentence_from_line_number(self._source, self._episode, self._line_number)
        self.screenshot_path, self.audio_clip_path = MediaUseCase.screenshot_and_audio_clip(
            self._source, self._episode, self._line_number)
        self._last_review = 0
        self._next_review = datetime.date.today()
        self._status = 'New'

        # TODO: Use this to decode the 'gloss' entry to a tuple of dictionaries with 'pos' and 'gloss' keys
        # gloss = ast.literal_eval(word_entry['gloss'][1:-1])

    def _create_from_deck_entry(self):
        pass


if __name__ == '__main__':
    card = Card('あっという間に 【あっというまに】')
    print(card.word)
