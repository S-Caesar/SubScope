import pandas as pd
import multiprocessing
from playsound import playsound
from PIL import Image
import io

from subscope.package.options.options import Options
from subscope.package.database.database import Database


class ReviewControl:
    _CARD_FORMAT = 'Card Format'
    _NEW_LIMIT = 'New Limit'
    _REVIEW_LIMIT = 'Review Limit'
    _STATUS = 'Status'
    _NEW = 'New'
    _REVIEW = 'Review'
    _NEXT_REVIEW = 'Next Review'
    _AUDIO = 'audio'
    _IMAGE = 'image'

    @staticmethod
    def deck_list():
        return Options.deck_list()

    @classmethod
    def load_deck(cls, deck_name):
        deck_path = Options.deck_folder_path() + '/' + deck_name + '.txt'
        deck = pd.read_csv(deck_path, sep='\t')
        deck = deck.sort_values(by=cls._NEXT_REVIEW).reset_index(drop=True)
        selected_cards = cls._select_cards(deck, deck_name)
        return selected_cards

    @classmethod
    def _select_cards(cls, deck, deck_name):
        deck_settings = Options.deck_settings()[deck_name]

        # TODO: Remove columns based on format settings
        card_format = deck_settings[cls._REVIEW_LIMIT]

        new_limit = int(deck_settings[cls._NEW_LIMIT])
        new_cards = cls._select_new_cards(deck, new_limit)

        review_limit = int(deck_settings[cls._REVIEW_LIMIT])
        review_cards = cls._select_review_cards(deck, review_limit)

        selected_cards = pd.concat([new_cards, review_cards])
        # Return the cards as a full sample, so they are shuffled
        return selected_cards.sample(frac=1)

    @classmethod
    def _select_new_cards(cls, deck, new_limit):
        return deck[deck[cls._STATUS] == cls._NEW].head(new_limit)

    @classmethod
    def _select_review_cards(cls, deck, review_limit):
        return deck[deck[cls._STATUS] == cls._REVIEW].head(review_limit)

    @classmethod
    def get_sentences(cls, source, episode, line_number):
        sentences = Database.sentence_from_line_number(source, episode, line_number)
        return sentences

    @classmethod
    def load_screenshot(cls, source, screenshot):
        image_file_path = Options.subtitles_folder_path() + '/' + source + '/' + cls._IMAGE + '/' + screenshot
        image = Image.open(image_file_path)
        image.thumbnail((475, 475))
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        return bio

    @classmethod
    def play_audio(cls, source, audio_file):
        audio_file_path = Options.subtitles_folder_path() + '/' + source + '/' + cls._AUDIO + '/' + audio_file
        audio = multiprocessing.Process(target=playsound, args=(audio_file_path,))
        audio.start()
        return audio


if __name__ == '__main__':
    ReviewControl.load_deck('SteinsGate')
