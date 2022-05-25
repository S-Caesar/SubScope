import PySimpleGUI as sg
from enum import Enum

from subscope.package.Options.options_control import OptionsControl


class Buttons(Enum):

    BACK = ('Back', True)
    APPLY = ('Apply Changes', True)

    def __init__(self, text, events):
        self.text = text
        self.events = events

    def create(self):
        return sg.Button(self.text, enable_events=self.events)


class OptionsView:

    _NAME = 'Options'
    _OPTIONS = OptionsControl().main_options()
    _OPTION_GROUPS = OptionsControl().main_option_groups()
    # TODO: these will need to be different for different themes...
    _TEXT_BUTTON_COLOURS = ['SteelBlue1'] + ['SteelBlue']*(len(_OPTION_GROUPS)-1)
    _THEMES = ['BlueMono', 'Dark2', 'DarkBlue14', 'DarkGrey4', 'DarkGrey5', 'DarkRed',
               'DarkTeal6', 'Default', 'Green', 'LightBrown11', 'LightBrown9']
    _SRS_COLOURING = ['On', 'Off']

    def _layout(self, options):
        # Main options column
        main_options = [[sg.Text(self._OPTION_GROUPS[x],
                                 enable_events=True,
                                 size=(11, 1),
                                 pad=(0, 6),
                                 key=f'-MAIN-{x}-',
                                 relief='raised',
                                 background_color=self._TEXT_BUTTON_COLOURS[x])]
                        for x in range(len(self._OPTION_GROUPS))]

        # Sub option, input box with the current path, and a button to browse
        path_options = []
        sub_options = options[self._OPTION_GROUPS[0]]
        for idx, sub_option in enumerate(sub_options):
            path_options.append([sg.Text(sub_option,
                                         size=(15, 1),
                                         pad=(0, 6),
                                         key=f'-SUB-{idx}-'),
                                 sg.In(default_text=sub_options[sub_option],
                                       size=(30, 2),
                                       pad=(0, 4),
                                       key=sub_option,
                                       readonly=True),
                                 sg.FolderBrowse(initial_folder=sub_options[sub_option])])

        # Deck name, new cards limit, review cards limit
        sub_options = options[self._OPTION_GROUPS[1]]
        columns = sub_options.columns
        deck = [[sg.Text(' ' * 30 + columns[0] + ' ' * 4 + columns[1])]]
        for row in range(len(sub_options)):
            deck.append([sg.Text(sub_options[columns[0]][row],
                                 size=(15, 1),
                                 pad=(0, 6),
                                 key=f'-DECK-{row}-'),
                         sg.Text(' ' * 0),
                         sg.In(default_text=sub_options[columns[1]][row],
                               size=(5, 1),
                               pad=(0, 6),
                               key=columns[0] + f'{row}'),
                         sg.Text(' ' * 7),
                         sg.In(default_text=sub_options[columns[2]][row],
                               size=(5, 1),
                               pad=(0, 6),
                               key=columns[1] + f'{row}')])

        # Theme option, dropdown with options
        sub_options = options[self._OPTION_GROUPS[2]]
        option_keys = list(sub_options.keys())
        theme_options = [[sg.Text(option_keys[0],
                                  size=(15, 1),
                                  pad=(0, 6),
                                  key=f'-THEME-{0}-'),
                          sg.Combo(self._THEMES,
                                   default_value=sub_options[option_keys[0]],
                                   pad=(0, 6),
                                   key=option_keys[0] + '0')],
                         [sg.Text(option_keys[1],
                                  size=(15, 1),
                                  pad=(0, 6),
                                  key=f'-THEME-{1}-'),
                          sg.Combo(self._SRS_COLOURING,
                                   default_value=sub_options[option_keys[1]],
                                   pad=(0, 6),
                                   key=option_keys[1] + '1')]]

        # Main buttons
        buttons = [[Buttons.BACK.create(),
                    Buttons.APPLY.create()]]

        # main layout: main options headings, sub options headings, settings
        layout = [[sg.Column(main_options, vertical_alignment='top'),
                   sg.VSeparator(),
                   sg.Column(path_options, size=(400, 150), key='-PATHS-', visible=True),
                   sg.Column(deck, size=(400, 150), key='-DECKS-', visible=False),
                   sg.Column(theme_options, size=(400, 150), key='-THEMES-', visible=False)],
                  [sg.Column(buttons)]]

        return layout

    def _window(self, options):
        window = sg.Window(self._NAME, layout=self._layout(options))
        return window

    def show(self):
        options = self._OPTIONS
        controller = OptionsControl()
        window = self._window(options)
        while True:
            event, values = window.Read()
            if event in [None, 'Back']:
                window.close()
                break

            # Change the section shown when one of the main options is selected
            sections = {'-MAIN-0-': '-PATHS-',
                        '-MAIN-1-': '-DECKS-',
                        '-MAIN-2-': '-THEMES-'}
            if event in sections:
                for section in sections:
                    if section == event:
                        window.Element(sections[section]).update(visible=True)
                        window.Element(section).update(background_color='SteelBlue1')
                    else:
                        window.Element(sections[section]).update(visible=False)
                        window.Element(section).update(background_color='SteelBlue')

            # TODO: add the update settings functionality
            # Update the settings files with user changes
            if event == Buttons.APPLY.text:
                controller.apply_changes()
                for option in self._OPTION_GROUPS:
                    for sub_option in self._OPTIONS[option]:
                        print(self._OPTIONS[option][sub_option])


if __name__ == '__main__':
    OptionsView().show()
