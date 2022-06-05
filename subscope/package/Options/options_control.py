import os

from subscope.package.options.options import Options


class OptionsControl:

    @staticmethod
    def main_options():
        return Options.main_options()

    @classmethod
    def main_option_groups(cls):
        return list(cls.main_options().keys())

    @staticmethod
    def apply_changes(updated_settings, seperator):
        """Use the keys in updated_settings to navigate to the matching key in the JSON"""
        current_settings = OptionsControl.main_options()
        for setting in updated_settings:
            temp_current_settings = current_settings
            if 'Browse' not in setting:
                setting_keys = setting.split(seperator)
                for key in setting_keys[:-1]:
                    temp_current_settings = temp_current_settings[key]
                temp_current_settings[setting_keys[-1]] = updated_settings[setting]

        Options.write_settings_file(current_settings)


if __name__ == '__main__':
    os.chdir('C:/Users/Steph/OneDrive/App/SubScope/subscope')
    print(OptionsControl.main_option_groups())
