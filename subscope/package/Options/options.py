import os
import subprocess
import json
from enum import Enum
from pathlib import Path


class Paths(Enum):

    DECK_FOLDER = ('Deck Folder', '/user/SRS/decks')
    SUBTITLES_FOLDER = ('Subtitles Folder', '/user/subtitles')
    OPTIONS_FOLDER = ('Options Folder', '/user/settings')
    ICHIRAN_FOLDER = ('Ichiran Folder', '')

    def __init__(self, key, path):
        self.key = key
        self.path = path


class Themes(Enum):

    MAIN_THEME = ('Main Theme', 'BlueMono')
    SRS_TEXT_COLOURING = ('SRS Text Colouring', 'On')

    def __init__(self, key, default):
        self.key = key
        self.default = default


class Decks(Enum):

    FORMAT = ('Card Format', 'Default')
    NEW_LIMIT = ('New Limit', 10)
    REVIEW_LIMIT = ('Review Limit', 100)

    def __init__(self, key, default):
        self.key = key
        self.default = default


class Options:

    _SETTINGS_PATH = str(Path(__file__).parent.parent.parent) + '/user/settings'
    _SETTINGS_FILE = 'settings.json'

    # Main option groups
    _DEFAULT_PATHS = 'Default Paths'
    _THEME_SETTINGS = 'UI Themes'
    _DECK_SETTINGS = 'Deck Settings'
    _DEFAULT_DECK = 'Default'

    # Cards
    _CARD_FORMATS = 'Card Formats'
    _FORMAT_NAME = 'Format Name'
    _DEFAULT_FORMAT = 'Default'
    _DEFAULT_SHORT_FORMAT = 'Short Format'
    _WORD_JAPANESE = 'b/wordJapanese'
    _PART_OF_SPEECH = 'partOfSpeech'
    _DEFINITION = 'r/definition'
    _INFO = 'r/info'
    _SCREENSHOT = 'r/screenshot'
    _FIELD_0 = 'field_0'
    _FIELD_1 = 'field_1'
    _FIELD_2 = 'field_2'
    _FIELD_3 = 'field_3'
    _FIELD_4 = 'field_4'

    @classmethod
    def create_settings_file(cls):
        """Create a default JSON format settings file"""
        project_path = os.getcwd()
        default_paths = {Paths.DECK_FOLDER.key: project_path + Paths.DECK_FOLDER.path,
                         Paths.SUBTITLES_FOLDER.key: project_path + Paths.SUBTITLES_FOLDER.path,
                         Paths.OPTIONS_FOLDER.key: project_path + Paths.OPTIONS_FOLDER.path,
                         Paths.ICHIRAN_FOLDER.key: cls._find_ichiran()}

        themes = {Themes.MAIN_THEME.key: Themes.MAIN_THEME.default,
                  Themes.SRS_TEXT_COLOURING.key: Themes.SRS_TEXT_COLOURING.default}

        deck_settings = {cls._DEFAULT_DECK:
                             {Decks.FORMAT.key: Decks.FORMAT.default,
                              Decks.NEW_LIMIT.key: Decks.NEW_LIMIT.default,
                              Decks.REVIEW_LIMIT.key: Decks.REVIEW_LIMIT.default}}

        card_formats = {cls._FORMAT_NAME:
                            {cls._DEFAULT_FORMAT:
                                 {cls._FIELD_0: cls._WORD_JAPANESE,
                                  cls._FIELD_1: cls._PART_OF_SPEECH,
                                  cls._FIELD_2: cls._DEFINITION,
                                  cls._FIELD_3: cls._INFO,
                                  cls._FIELD_4: cls._SCREENSHOT},
                             cls._DEFAULT_SHORT_FORMAT:
                                 {cls._FIELD_0: cls._WORD_JAPANESE,
                                  cls._FIELD_1: cls._DEFINITION,
                                  cls._FIELD_2: cls._SCREENSHOT}}}

        settings_file = {cls._DEFAULT_PATHS: default_paths,
                         cls._THEME_SETTINGS: themes,
                         cls._DECK_SETTINGS: deck_settings,
                         cls._CARD_FORMATS: card_formats}

        cls.write_settings_file(settings_file)

    @classmethod
    def _find_ichiran(cls):
        path = None
        target = 'local-projects'
        ichiran = 'ichiran'
        start = 'C:/Users/'

        # Try to find ichiran in the current settings path
        filepath = cls._SETTINGS_PATH + '/' + cls._SETTINGS_FILE
        if os.path.isfile(filepath):
            ichiran = subprocess.check_output('ichiran-cli -f ' + '何しての', shell=True, cwd=cls.ichiran_path())
        else:
            for directory_path, sub_directories, files in os.walk(start):
                if target in sub_directories:
                    try:
                        path = os.path.join(directory_path, target) + '/' + ichiran
                        ichiran = subprocess.check_output('ichiran-cli -f ' + '何しての', shell=True, cwd=path)
                        break
                    except subprocess.CalledProcessError:
                        continue

        if ichiran is None:
            # TODO: prompt the user to find the quicklisp folder themselves
            print('No valid paths to ichiran')
        else:
            print('Ichiran found')
        return path

    @classmethod
    def _read_settings_file(cls):
        filepath = cls._SETTINGS_PATH + '/' + cls._SETTINGS_FILE
        if not os.path.isfile(filepath):
            cls.create_settings_file()
        file = open(filepath)
        return json.load(file)

    @classmethod
    def main_options(cls):
        return cls._read_settings_file()

    @classmethod
    def _path_settings(cls):
        return cls._read_settings_file()[cls._DEFAULT_PATHS]

    @classmethod
    def deck_folder_path(cls):
        return cls._path_settings()[Paths.DECK_FOLDER.key]

    @classmethod
    def subtitles_folder_path(cls):
        return cls._path_settings()[Paths.SUBTITLES_FOLDER.key]

    @classmethod
    def options_folder_path(cls):
        return cls._path_settings()[Paths.OPTIONS_FOLDER.key]

    @classmethod
    def ichiran_path(cls):
        return cls._path_settings()[Paths.ICHIRAN_FOLDER.key]

    @classmethod
    def _theme_settings(cls):
        return cls._read_settings_file()[cls._THEME_SETTINGS]

    @classmethod
    def main_theme(cls):
        return cls._theme_settings()[Themes.MAIN_THEME.key]

    @classmethod
    def srs_colouring(cls):
        return cls._theme_settings()[Themes.SRS_TEXT_COLOURING.key]

    @classmethod
    def deck_settings(cls):
        return cls._read_settings_file()[cls._DECK_SETTINGS]

    @classmethod
    def card_formats(cls):
        return cls._read_settings_file()[cls._CARD_FORMATS]

    @classmethod
    def write_settings_file(cls, settings):
        output_file = cls._SETTINGS_PATH + '/' + cls._SETTINGS_FILE
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
