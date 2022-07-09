import random
import datetime
import ast
from enum import Enum

from subscope.package.database.database import Database
from subscope.package.utilities.media_use_case import MediaUseCase


class CardHeading(Enum):
    REVIEW_STATE = 'Review State'
    SOURCE = 'Source'
    EPISODE = 'Analysed Output'
    LINE_NUMBER = 'Line Number'
    WORD = 'Word'
    GLOSS = 'Gloss'
    AUDIO_CLIP = 'Audio Clip'
    SCREENSHOT = 'Screenshot'
    SCORE = 'Score'
    LAST_REVIEW = 'Last Review'
    NEXT_REVIEW = 'Next Review'
    STATUS = 'Status'

    def __init__(self, text):
        self.text = text


class Card:
    _CARD_PART = 'pos'
    _CARD_GLOSS = 'gloss'
    _CARD_INFO = 'info'

    def __init__(self, word=None, deck_entry=None):
        self.word = word
        self._deck_entry = deck_entry
        if word is not None:
            self._create_from_word()
        else:
            self._create_from_deck_entry(deck_entry)

    def entry(self):
        # TODO: At the moment, these don't tie in with the CardHeading names, so both need to be changed together
        entry = [self._review_state, self._source, self._episode, self._line_number, self.word, self._gloss,
                 self.audio_clip_path, self.screenshot_path, self._score, self._last_review,
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
        self.screenshot_path, self.audio_clip_path = MediaUseCase.screenshot_and_audio_clip(
            self._source, self._episode, self._line_number)
        self._last_review = 0
        self._next_review = datetime.date.today()
        self._status = 'New'

    def _create_from_deck_entry(self, deck_entry):
        self.review_state = deck_entry[CardHeading.REVIEW_STATE.text]
        self.source = deck_entry[CardHeading.SOURCE.text]
        self.episode = deck_entry[CardHeading.EPISODE.text]
        self.line_number = deck_entry[CardHeading.LINE_NUMBER.text]
        self.word = deck_entry[CardHeading.WORD.text]
        self.gloss = deck_entry[CardHeading.GLOSS.text]
        self.audio_clip = deck_entry[CardHeading.AUDIO_CLIP.text]
        self.screenshot = deck_entry[CardHeading.SCREENSHOT.text]
        self.score = deck_entry[CardHeading.SCORE.text]
        self.last_review = deck_entry[CardHeading.LAST_REVIEW.text]
        self.next_review = deck_entry[CardHeading.NEXT_REVIEW.text]
        self.status = deck_entry[CardHeading.STATUS.text]

    def split_glossary(self):
        gloss = ast.literal_eval(self.gloss[1:-1])
        # TODO: Provide all definitions, instead of just one - maybe with arrow buttons to change display
        if self._CARD_PART not in gloss:
            gloss = gloss[0]

        for item in [self._CARD_PART, self._CARD_GLOSS, self._CARD_INFO]:
            if item not in gloss:
                gloss[item] = ''
        return gloss

    @property
    def part_of_speech(self):
        gloss = self.split_glossary()
        return gloss[self._CARD_PART]


if __name__ == '__main__':
    card = Card('あっという間に 【あっというまに】')
    print(card.word)
