import os

from subscope.package.options.options import Options


class DecksControl:

    @staticmethod
    def deck_list():
        deck_list = os.listdir(Options.deck_folder_path())
        for idx, deck in enumerate(deck_list):
            deck_list[idx] = deck.replace('.txt', '')
        return deck_list

    @staticmethod
    def subtitles_list():
        subtitles_path = Options.subtitles_folder_path()
        subtitle_list = [item for item in os.listdir(subtitles_path)
                         if os.path.isdir(os.path.join(subtitles_path, item))]
        return subtitle_list

    @staticmethod
    def create_deck():
        pass
