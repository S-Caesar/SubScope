import pandas as pd
import multiprocessing
from playsound import playsound
from PIL import Image
import io
from datetime import datetime, date, timedelta
import ast

from subscope.settings.settings import Settings
from subscope.database.database import Database
from subscope.decks.card import Card


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
    _AUDIO_FOLDER = 'audio'
    _AUDIO = 'Audio Clip'
    _IMAGE = 'image'
    _SOURCE = 'Source'
    _TEXT = 'text'
    _READING = 'reading'
    _CARD_PART = 'pos'
    _SUFFIX = 'suffix'
    _CARD_GLOSS = 'gloss'
    _NO_ENTRY = 'No Entry'

    # I use this character in place of string apostrophes when dealing with the Ichiran output
    _SUBSTITUTE = '^'
    _APOSTROPHE = '\''

    deck_name = None
    deck = None
    card = None
    card_index = None
    _audio = None

    sentences_word_entries = [pd.DataFrame([]), pd.DataFrame([])]

    @staticmethod
    def deck_list():
        return Settings.deck_list()

    def load_deck(self, deck_name):
        self.deck_name = deck_name
        deck_path = Settings.deck_folder_path() + '/' + self.deck_name + '.txt'
        deck = pd.read_csv(deck_path, sep='\t')
        deck = deck.sort_values(by=self._NEXT_REVIEW)
        selected_cards = self._select_cards(deck)
        self.deck = selected_cards

    def _select_cards(self, deck):
        deck_settings = Settings.deck_settings()[self.deck_name]

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
        if len(cards.index) > 0:
            self.card_index = cards.index.tolist()[0]
            self.card = Card(deck_entry=cards.iloc[0].to_dict())
        else:
            self.card = None
            self.card_index = None

    def remaining_cards(self):
        return len(self.deck.index)

    def get_sentence_data(self):
        source = self.card.source
        episode = self.card.episode
        line_number = self.card.line_number

        sentences = Database.sentence_from_line_number(source, episode, line_number)
        sentences_word_entries = Database.word_entries_from_line_number(source, episode, line_number)

        self.sentences_word_entries = [pd.DataFrame([]), pd.DataFrame([])]
        for index, entries in enumerate(sentences_word_entries):
            if len(entries) != 0 and self._TEXT in entries.columns:
                self.sentences_word_entries[index] = self._order_words_to_match_sentence(sentences[index], entries)
        return self.sentences_word_entries

    @classmethod
    def _order_words_to_match_sentence(cls, sentence, entries):
        ordered_sentence = []
        word_list = entries[cls._TEXT].tolist()
        while len(sentence) > 0:
            added = False
            for index, word in enumerate(word_list):
                if sentence[:len(word)] == word:
                    ordered_sentence.append(word)
                    sentence = sentence[len(word):]
                    del word_list[index]
                    added = True
                    break

            if not added:
                ordered_sentence.append(sentence[0])
                if len(sentence) > 1:
                    sentence = sentence[1:]
                else:
                    break

        for word in ordered_sentence:
            target_index = entries[(entries[cls._TEXT] == word)].index.tolist()
            if len(target_index) != 0:
                if len(target_index) > 1:
                    target_index = [target_index[0]]
                index = entries.index.tolist()
                index.pop(target_index[0])
                entries = entries.reindex(index + target_index)
            else:
                entries = pd.concat([entries, pd.DataFrame([word], columns=[cls._TEXT])])
            entries = entries.reset_index(drop=True)

        return entries.fillna(cls._NO_ENTRY)

    def retrieve_entry(self, clicked_word, sentence_index):
        sentences_word_entries = self.sentences_word_entries[sentence_index]
        word_data = sentences_word_entries[sentences_word_entries[self._TEXT] == clicked_word]
        reading = word_data[self._READING].tolist()[0]
        gloss = word_data[self._CARD_GLOSS].tolist()[0]
        gloss = self._format_json_glossary(gloss)
        if gloss == self._NO_ENTRY and self._SUFFIX in word_data:
            gloss = str(word_data[self._SUFFIX].to_list()[0])

        entry = {self._READING: reading,
                 self._CARD_GLOSS: gloss}

        return entry

    @classmethod
    def _format_json_glossary(cls, gloss):
        if cls._NO_ENTRY not in gloss:
            gloss = ast.literal_eval(gloss[1:-1])
            if cls._CARD_PART in gloss:
                gloss = [gloss]

            str_gloss = ''
            for definition in gloss:
                if definition != cls._NO_ENTRY:
                    str_gloss += definition[cls._CARD_PART] + '\n' + definition[cls._CARD_GLOSS] + '\n\n'
            str_gloss = str_gloss.replace(cls._SUBSTITUTE, cls._APOSTROPHE)
        else:
            str_gloss = cls._NO_ENTRY
        return str_gloss

    def load_screenshot(self):
        source = self.card.source
        screenshot = self.card.screenshot

        image_file_path = Settings.subtitles_folder_path() + '/' + source + '/' + self._IMAGE + '/' + screenshot
        image = Image.open(image_file_path)
        image.thumbnail((475, 475))
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        image = bio.getvalue()
        return image

    def play_audio(self):
        source = self.card.source
        audio_file = self.card.audio_clip
        self.stop_audio()
        audio_file_path = Settings.subtitles_folder_path() + '/' + source + '/' + self._AUDIO_FOLDER + '/' + audio_file
        self._audio = multiprocessing.Process(target=playsound, args=(audio_file_path,))
        self._audio.start()

    def stop_audio(self):
        if self._audio:
            self._audio.terminate()

    def record_response(self, response_score):
        self.deck.loc[self.card_index, self._STATE] = 1

        current_score = self.deck[self._SCORE][self.card_index]
        self.deck.loc[self.card_index, self._SCORE] = self._adjust_score(response_score, current_score)

        self._update_review_dates(response_score)

    def _update_review_dates(self, response_score):
        if str(self.deck[self._LAST_REVIEW][self.card_index]) == '0':
            interval = 1
        else:
            next_review = datetime.strptime(str(self.deck.loc[self.card_index, self._NEXT_REVIEW]), '%Y-%m-%d')
            last_review = datetime.strptime(str(self.deck.loc[self.card_index, self._LAST_REVIEW]), '%Y-%m-%d')
            interval = next_review - last_review
            if interval.days < 1:
                interval = 1
            else:
                interval = interval.days

        if response_score == 0:
            new_interval = 1
        else:
            new_interval = round(interval * self.deck[self._SCORE][self.card_index])

        self.deck.loc[self.card_index, self._LAST_REVIEW] = date.today()
        self.deck.loc[self.card_index, self._NEXT_REVIEW] = self.deck.loc[self.card_index, self._LAST_REVIEW] \
                                                            + timedelta(days=new_interval)
        self.deck.loc[self.card_index, self._STATUS] = self._REVIEW

    def update_deck(self):
        deck_path = Settings.deck_folder_path() + '/' + self.deck_name + '.txt'
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

    def mark_known(self):
        self.deck.loc[self.card_index, self._STATE] = 1
        self.deck.loc[self.card_index, self._STATUS] = self._KNOWN

    def mark_suspended(self):
        self.deck.loc[self.card_index, self._STATE] = 1
        self.deck.loc[self.card_index, self._STATUS] = self._SUSPENDED
