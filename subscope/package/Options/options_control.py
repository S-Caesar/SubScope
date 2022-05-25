import os

from subscope.package.Options.options import Options


class OptionsControl:

    @staticmethod
    def main_options():
        main_options = {Options().DEFAULT_PATHS_NAME: Options().path_options(),
                        Options().DECK_SETTINGS_NAME: Options().deck_settings(),
                        Options().THEME_SETTINGS_NAME: Options().theme_settings()}
        return main_options

    @classmethod
    def main_option_groups(cls):
        headings = list(cls.main_options().keys())
        return headings

    def apply_changes(self):
        pass


if __name__ == '__main__':
    os.chdir('C:/Users/Steph/OneDrive/App/SubScope/subscope')
    OptionsControl.main_options()