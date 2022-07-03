import pandas as pd
import multiprocessing
from playsound import playsound
from PIL import Image
import io
from datetime import datetime, date, timedelta

from subscope.package.options.options import Options
from subscope.package.database.database import Database


class ReviewControl:
    _CARD_FORMAT = 'Card Format'
    _NEW_LIMIT = 'New Limit'
    _REVIEW_LIMIT = 'Review Limit'
    _STATE = 'Review State'
    _SCORE = 'Score'
    _KNOWN = 'Known'
    _SUSPENDED = 'Suspended'
    _STATUS = 'Status'
    _NEW = 'New'
    _REVIEW = 'Review'
    _LAST_REVIEW = 'Last Review'
    _NEXT_REVIEW = 'Next Review'
    _AUDIO = 'audio'
    _IMAGE = 'image'

    deck_name = None
    deck = None
    _audio = None

    @staticmethod
    def deck_list():
        return Options.deck_list()

    def load_deck(self, deck_name):
        self.deck_name = deck_name
        deck_path = Options.deck_folder_path() + '/' + self.deck_name + '.txt'
        deck = pd.read_csv(deck_path, sep='\t')
        deck = deck.sort_values(by=self._NEXT_REVIEW)
        selected_cards = self._select_cards(deck)
        self.deck = selected_cards

    def _select_cards(self, deck):
        deck_settings = Options.deck_settings()[self.deck_name]

        # TODO: Remove columns based on format settings
        card_format = deck_settings[self._REVIEW_LIMIT]

        new_limit = int(deck_settings[self._NEW_LIMIT])
        new_cards = self._select_new_cards(deck, new_limit)

        review_limit = int(deck_settings[self._REVIEW_LIMIT])
        review_cards = self._select_review_cards(deck, review_limit)

        selected_cards = pd.concat([new_cards, review_cards])
        # Return the cards as a full sample, so they are shuffled
        return selected_cards.sample(frac=1)

    @classmethod
    def _select_new_cards(cls, deck, new_limit):
        return deck[deck[cls._STATUS] == cls._NEW].head(new_limit)

    @classmethod
    def _select_review_cards(cls, deck, review_limit):
        today = datetime.today()
        to_review = deck[deck[cls._STATUS] == cls._REVIEW]
        review_cards = to_review[to_review[cls._NEXT_REVIEW].astype('datetime64[D]') <= today].head(review_limit)
        return review_cards

    def load_card(self):
        cards = self.deck[self.deck[self._STATE] == 0]
        index = cards.index.tolist()[0]
        card = cards.iloc[0]
        return card, index

    def remaining_cards(self):
        return len(self.deck.index)

    @classmethod
    def get_sentences(cls, source, episode, line_number):
        sentences = Database.sentence_from_line_number(source, episode, line_number)
        return sentences

    @classmethod
    def get_sentence_data(cls, source, episode, line_number):
        sentence_data = Database.sentence_data_from_line_number(source, episode, line_number)
        if len(sentence_data) == 1:
            sentence_data.append('')
        return sentence_data

    @classmethod
    def load_screenshot(cls, source, screenshot):
        image_file_path = Options.subtitles_folder_path() + '/' + source + '/' + cls._IMAGE + '/' + screenshot
        image = Image.open(image_file_path)
        image.thumbnail((475, 475))
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        return bio

    def play_audio(self, source, audio_file):
        self.stop_audio()
        audio_file_path = Options.subtitles_folder_path() + '/' + source + '/' + self._AUDIO + '/' + audio_file
        self._audio = multiprocessing.Process(target=playsound, args=(audio_file_path,))
        self._audio.start()

    def stop_audio(self):
        if self._audio:
            self._audio.terminate()

    def record_response(self, index, response_score):
        self.deck.loc[index, self._STATE] = 1

        current_score = self.deck[self._SCORE][index]
        self.deck.loc[index, self._SCORE] = self._adjust_score(response_score, current_score)

        self._update_review_dates(index, response_score)

    def _update_review_dates(self, index, response_score):
        if str(self.deck[self._LAST_REVIEW][index]) == '0':
            interval = 1
        else:
            next_review = datetime.strptime(str(self.deck.loc[index, self._NEXT_REVIEW]), '%Y-%m-%d')
            last_review = datetime.strptime(str(self.deck.loc[index, self._LAST_REVIEW]), '%Y-%m-%d')
            interval = next_review - last_review
            if interval.days < 1:
                interval = 1
            else:
                interval = interval.days

        if response_score == 0:
            new_interval = 1
        else:
            new_interval = round(interval * self.deck[self._SCORE][index])

        self.deck.loc[index, self._LAST_REVIEW] = date.today()
        self.deck.loc[index, self._NEXT_REVIEW] = self.deck.loc[index, self._LAST_REVIEW] + timedelta(days=new_interval)
        self.deck.loc[index, self._STATUS] = self._REVIEW

    def update_deck(self):
        deck_path = Options.deck_folder_path() + '/' + self.deck_name + '.txt'
        full_deck = pd.read_csv(deck_path, sep='\t')
        for index in self.deck.index.tolist():
            self.deck.loc[index, self._STATE] = 0
            full_deck.loc[index, :] = self.deck.loc[index, :]
        full_deck.to_csv(deck_path, sep='\t', index=None)

    @staticmethod
    def _adjust_score(response_score, current_score):
        updated_score = round(current_score + (0.1 - (3 - response_score) * (0.1 + (3 - response_score) * 0.06)), 3)
        if updated_score < 1.3:
            updated_score = 1.3
        return updated_score

    def mark_known(self, index):
        self.deck.loc[index, self._STATE] = 1
        self.deck.loc[index, self._STATUS] = self._KNOWN

    def mark_suspended(self, index):
        self.deck.loc[index, self._STATE] = 1
        self.deck.loc[index, self._STATUS] = self._SUSPENDED
