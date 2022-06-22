import os

from subscope.package.options.options import Options
from subscope.package.decks.deck import Deck


class DecksControl:

    @staticmethod
    def deck_list():
        return Options.deck_list()

    @staticmethod
    def formats_list():
        return list(Options.card_formats().keys())

    @staticmethod
    def subtitles_list():
        subtitles_path = Options.subtitles_folder_path()
        subtitle_list = [item for item in os.listdir(subtitles_path)
                         if os.path.isdir(os.path.join(subtitles_path, item))]
        return subtitle_list

    @staticmethod
    def create_deck(deck_name, new_limit, review_limit, card_format, source=None, target_comp=None):
        Deck.create(deck_name, new_limit, review_limit, card_format, source, target_comp)

    @staticmethod
    def delete_deck(deck_name):
        deck_folder = Options.deck_folder_path()
        os.remove(deck_folder + '/' + deck_name + '.txt')
        Options.remove_deck_from_settings(deck_name)


if __name__ == '__main__':
    DecksControl.delete_deck('example.txt')
