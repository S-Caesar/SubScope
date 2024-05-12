import os

from subscope.settings.settings import Settings
from subscope.decks.deck import Deck
from subscope.database.database import Database


class DecksControl:

    @staticmethod
    def deck_list():
        return Settings.deck_list()

    @staticmethod
    def formats_list():
        return list(Settings.card_formats().keys())

    @staticmethod
    def subtitles_list():
        subtitles_path = Settings.subtitles_folder_path()
        subtitle_list = [item for item in os.listdir(subtitles_path)
                         if os.path.isdir(os.path.join(subtitles_path, item))]
        return subtitle_list

    @staticmethod
    def create_deck(deck_name, new_limit, review_limit, card_format, source=None, target_comp=None):
        Deck.create(deck_name, new_limit, review_limit, card_format, source, target_comp)

    @staticmethod
    def delete_deck(deck_name):
        deck_folder = Settings.deck_folder_path()
        os.remove(deck_folder + '/' + deck_name + '.txt')
        Settings.remove_deck_from_settings(deck_name)

    @staticmethod
    def get_word_data():
        return Database.get_words_data_only()

    @staticmethod
    def add_cards_to_deck(deck_name, words):
        Deck.add_cards(deck_name, words)

    @staticmethod
    def read_deck(deck_name):
        return Deck.read_deck(deck_name)


if __name__ == '__main__':
    DecksControl.delete_deck('example.txt')
