import os

from subscope.settings.settings import Settings


class SettingsControl:

    @staticmethod
    def main_options():
        return Settings.main_options()

    @classmethod
    def main_option_groups(cls):
        return list(cls.main_options().keys())

    @staticmethod
    def apply_changes(updated_settings, seperator):
        """Use the keys in updated_settings to navigate to the matching key in the JSON"""
        current_settings = SettingsControl.main_options()
        for setting in updated_settings:
            temp_current_settings = current_settings
            if 'Browse' not in setting:
                setting_keys = setting.split(seperator)
                for key in setting_keys[:-1]:
                    temp_current_settings = temp_current_settings[key]
                temp_current_settings[setting_keys[-1]] = updated_settings[setting]

        Settings.write_settings_file(current_settings)


if __name__ == '__main__':
    os.chdir('/subscope')
    print(SettingsControl.main_option_groups())
