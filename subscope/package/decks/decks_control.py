import os

from subscope.package.options.options import Options


class DecksControl:

    @staticmethod
    def deck_list():
        return os.listdir(Options.deck_folder_path())
