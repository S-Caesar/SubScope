import PySimpleGUI as sg
from enum import Enum

from subscope.options.options_control import OptionsControl


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
    _OPTION_GROUPS = OptionsControl().main_option_groups()
    # TODO: these will need to be different for different themes...
    _TEXT_BUTTON_COLOURS = ['SteelBlue1'] + ['SteelBlue']*(len(_OPTION_GROUPS)-1)
    _THEMES = ['BlueMono', 'Dark2', 'DarkBlue14', 'DarkGrey4', 'DarkGrey5', 'DarkRed',
               'DarkTeal6', 'Default', 'Green', 'LightBrown11', 'LightBrown9']
    _SRS_COLOURING = ['On', 'Off']

    _PATHS_WINDOW = '-PATHS-'
    _THEMES_WINDOW = '-THEMES-'
    _DECKS_WINDOW = '-DECKS-'
    _CARDS_WINDOW = '-CARDS-'

    _SEP = '>'

    def _layout(self, options):
        # Main options column
        main_options = [[sg.Text(option,
                                 enable_events=True,
                                 size=(11, 1),
                                 pad=(0, 6),
                                 key=option,
                                 relief='raised',
                                 background_color=self._TEXT_BUTTON_COLOURS[idx])]
                        for idx, option in enumerate(self._OPTION_GROUPS)]

        # Sub option, input box with the current path, and a button to browse
        option_group = self._OPTION_GROUPS[0]
        path_options = []
        sub_options = options[option_group]
        for idx, sub_option in enumerate(sub_options):
            path_options.append([sg.Text(sub_option,
                                         size=(15, 1),
                                         pad=(0, 6)),
                                 sg.In(default_text=sub_options[sub_option],
                                       size=(30, 2),
                                       pad=(0, 4),
                                       key=f'{option_group}{self._SEP}{sub_option}',
                                       readonly=True),
                                 sg.FolderBrowse(initial_folder=sub_options[sub_option])])

        # Theme option, dropdown with options
        option_group = self._OPTION_GROUPS[1]
        sub_options = options[option_group]
        option_keys = list(sub_options.keys())
        theme_options = [[sg.Text(option_keys[0],
                                  size=(15, 1),
                                  pad=(0, 6)),
                          sg.Combo(self._THEMES,
                                   default_value=sub_options[option_keys[0]],
                                   pad=(0, 6),
                                   key=f'{option_group}{self._SEP}{option_keys[0]}')],

                         [sg.Text(option_keys[1],
                                  size=(15, 1),
                                  pad=(0, 6)),
                          sg.Combo(self._SRS_COLOURING,
                                   default_value=sub_options[option_keys[1]],
                                   pad=(0, 6),
                                   key=f'{option_group}{self._SEP}{option_keys[1]}')]]

        # Deck name, new cards limit, review cards limit
        option_group = self._OPTION_GROUPS[2]
        deck_settings = options[option_group]
        decks = list(deck_settings.keys())
        sub_options = deck_settings[decks[0]]
        sub_option_headings = list(sub_options.keys())

        deck_layout = [[sg.Text(' ' * 30 + sub_option_headings[0] + ' ' * 4 + sub_option_headings[1])]]
        for deck in decks:
            deck_layout.append([sg.Text(deck_settings[deck][sub_option_headings[0]],
                                        size=(15, 1),
                                        pad=(0, 6)),
                                sg.Text(' ' * 0),
                                sg.In(default_text=deck_settings[deck][sub_option_headings[1]],
                                      size=(5, 1),
                                      pad=(0, 6),
                                      key=f'{option_group}{self._SEP}{deck}{self._SEP}{sub_option_headings[1]}'),
                                sg.Text(' ' * 7),
                                sg.In(default_text=deck_settings[deck][sub_option_headings[2]],
                                      size=(5, 1),
                                      pad=(0, 6),
                                      key=f'{option_group}{self._SEP}{deck}{self._SEP}{sub_option_headings[2]}')])

        # Card formats
        card_layout = [[]]

        # Main buttons
        buttons = [[Buttons.BACK.create(),
                    Buttons.APPLY.create()]]

        # Main layout: all sections are created, and then shown / hidden when UI text is clicked
        layout = [[sg.Column(main_options, vertical_alignment='top'),
                   sg.VSeparator(),
                   sg.Column(path_options, size=(400, 150), key=self._PATHS_WINDOW, visible=True),
                   sg.Column(theme_options, size=(400, 150), key=self._THEMES_WINDOW, visible=False),
                   sg.Column(deck_layout, size=(400, 150), key=self._DECKS_WINDOW, visible=False),
                   sg.Column(card_layout, size=(400, 150), key=self._CARDS_WINDOW, visible=False)],
                  [sg.Column(buttons)]]

        return layout

    def _window(self, options):
        window = sg.Window(self._NAME, layout=self._layout(options))
        return window

    def show(self):
        options = OptionsControl().main_options()
        controller = OptionsControl()
        window = self._window(options)
        while True:
            event, values = window.Read()
            if event in [None, Buttons.BACK.text]:
                window.close()
                break

            # Change the section shown when one of the main options is selected
            sections = {self._OPTION_GROUPS[0]: self._PATHS_WINDOW,
                        self._OPTION_GROUPS[1]: self._THEMES_WINDOW,
                        self._OPTION_GROUPS[2]: self._DECKS_WINDOW,
                        self._OPTION_GROUPS[3]: self._CARDS_WINDOW}
            if event in sections:
                for section in sections:
                    if section == event:
                        window.Element(sections[section]).update(visible=True)
                        window.Element(section).update(background_color=self._TEXT_BUTTON_COLOURS[0])
                    else:
                        window.Element(sections[section]).update(visible=False)
                        window.Element(section).update(background_color=self._TEXT_BUTTON_COLOURS[1])

            # Update the settings files with user changes
            if event == Buttons.APPLY.text:
                # TODO: Have the window update to show the selected UI theme if changed
                controller.apply_changes(values, self._SEP)
