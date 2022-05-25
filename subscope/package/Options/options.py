import os
import pandas as pd


class Options:
    os.chdir('C:\\Users\\Steph\\OneDrive\\App\\SubScope\\subscope')
    _SETTINGS_PATH = os.getcwd() + '/user/settings'
    DEFAULT_PATHS_NAME = 'Default Paths'
    _DEFAULT_PATHS_FILE = 'default_paths.txt'
    DECK_SETTINGS_NAME = 'Deck Settings'
    _DECK_SETTINGS_FILE = 'deckSettings.txt'
    THEME_SETTINGS_NAME = 'UI Themes'
    _THEME_SETTINGS_FILE = 'themesUI.txt'
    _DECK_FORMATS_FILE = 'cardFormats.txt'

    def path_options(self):
        file = pd.read_csv(self._SETTINGS_PATH + '/' + self._DEFAULT_PATHS_FILE, sep='\t')
        path_options = dict(zip(file['Option'], file['Setting']))
        return path_options

    def deck_folder_path(self):
        return self.path_options()['Deck Folder']

    def source_folder_path(self):
        return self.path_options()['Source Folder']

    def options_folder_path(self):
        return self.path_options()['Options Folder']

    def ichiran_path(self):
        return self.path_options()['Ichiran Path']

    def theme_settings(self):
        file = pd.read_csv(self._SETTINGS_PATH + '/' + self._THEME_SETTINGS_FILE, sep='\t')
        theme_settings = dict(zip(file['Option'], file['Setting']))
        return theme_settings

    def main_theme(self):
        return self.theme_settings()['Main Theme']

    def srs_colouring(self):
        return self.theme_settings()['SRS Text Colouring']

    def deck_settings(self):
        file = pd.read_csv(self._SETTINGS_PATH + '/' + self._DECK_SETTINGS_FILE, sep='\t')
        return file

    def deck_formats(self, deck_format):
        file = pd.read_csv(self._SETTINGS_PATH + '/' + self._DECK_FORMATS_FILE, sep='\t')
        settings = file[file['Deck Name'] == deck_format].reset_index(drop=True)
        return settings


if __name__ == '__main__':
    print(Options().path_options())
