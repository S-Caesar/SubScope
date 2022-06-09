import PySimpleGUI as sg
from enum import Enum

from subscope.package.decks.decks_control import DecksControl


class Text(Enum):

    # Main Window
    TITLE = ('Manage Decks', 'any 14')
    CREATE_DECK = 'Create a new deck'
    MODIFY_DECK = 'Modify an existing deck'

    # Create Window
    CREATE_TITLE = ('Create Deck', 'any 14')
    EMPTY_DECK = 'Empty Deck'
    AUTOFILL_DECK = 'Autofill Deck'
    DECK_NAME = ('Deck Name:', None, (12, 1))
    NEW_LIMIT = ('New Limit:', None, (12, 1))
    REVIEW_LIMIT = ('Review Limit:', None, (12, 1))
    SOURCE = ('Source:', None, (12, 1))
    TARGET_COMP = 'Target Comprehension:'

    def __init__(self, text, font=None, size=None):
        self.text = text
        self.font = font
        if size is None:
            self.size = (None, None)
        else:
            self.size = size

    def create(self):
        return sg.Text(self.text,
                       font=self.font,
                       size=self.size)


class Button(Enum):

    # Main Window
    CREATE_NEW_DECK = ('Create New Deck', (16, 1))
    ADD_CARDS = ('Add Cards', (16, 1))
    REMOVE_CARDS = ('Remove Cards', (16, 1))
    DECK_STATS = ('Deck Stats', (16, 1))
    DELETE_DECK = ('Delete Deck', (16, 1))
    BACK = ('Back', None)

    # Create Window
    CREATE_DECK = ('Create Deck', None)

    def __init__(self, text, size):
        self.text = text
        if size is None:
            self.size = (None, None)
        else:
            self.size = size

    def create(self):
        button = sg.Button(self.text,
                           size=self.size)
        return button


class Inputbox(Enum):

    DECK_NAME = ((14, 1), 'DECK_NAME_INPUT', '')
    NEW_LIMIT = ((5, 1), 'NEW_LIMIT_INPUT', '')
    REVIEW_LIMIT = ((5, 1), 'REVIEW_LIMIT_INPUT', '')
    TARGET_COMP = ((3, 1), 'TARGET_COMP_INPUT', '')

    def __init__(self, size, key, default):
        self.size = size
        self.key = key
        self.default = default

    def create(self):
        return sg.Input(default_text=self.default,
                        key=self.key,
                        size=self.size)


class DecksView:

    _NAME = 'Manage Decks'
    _DECK_NAME = 'DECK_NAME'
    _CREATE_WINDOW = 'CREATE'
    _ADD_WINDOW = 'ADD'
    _REMOVE_WINDOW = 'REMOVE'
    _STATS_WINDOW = 'STATS'
    _DELETE_WINDOW = 'DELETE'
    _STATUS = 'STATUS'

    # Create window
    _SUBTITLE_SOURCE = 'SUBTITLE_SOURCE'
    _DECK_NAME_EXISTS = 'Deck name already exists'
    _DECK_CREATED = 'Deck created!'
    _BLANK_NAME = 'Deck Name is blank'
    _BLANK_SOURCE = 'Autofill checked, but no source selected'

    def __init__(self):
        self._status = ''

    def _layout(self):
        headings = [[Text.TITLE.create()]]

        create_deck = [[Text.CREATE_DECK.create()],
                       [Button.CREATE_NEW_DECK.create()],
                       [sg.Text('')],
                       [Text.MODIFY_DECK.create()]]

        deck_list = DecksControl.deck_list()
        modify_deck = [[sg.Combo(deck_list,
                                 default_value=deck_list[0],
                                 enable_events=True,
                                 key=self._DECK_NAME)],
                       [Button.ADD_CARDS.create()],
                       [Button.REMOVE_CARDS.create()],
                       [Button.DECK_STATS.create()],
                       [Button.DELETE_DECK.create()]]

        add_window = [[sg.Text('Add Cards to Deck')]]

        remove_window = [[sg.Text('Remove Cards')]]

        stats_window = [[sg.Text('Display Stats')]]

        delete_window = [[sg.Text('Delete Selected Deck?')]]

        window_height = 300
        layout = [[sg.Column(headings + create_deck + modify_deck),
                   sg.VSeperator(),
                   sg.Column(self._create_window(), size=(400, window_height), key=self._CREATE_WINDOW, visible=True),
                   sg.Column(add_window, size=(400, window_height), key=self._ADD_WINDOW, visible=False),
                   sg.Column(remove_window, size=(400, window_height), key=self._REMOVE_WINDOW, visible=False),
                   sg.Column(stats_window, size=(400, window_height), key=self._STATS_WINDOW, visible=False),
                   sg.Column(delete_window, size=(400, window_height), key=self._DELETE_WINDOW, visible=False)],
                  [sg.Column([[Button.BACK.create()]])]]
        return layout

    def _create_window(self):
        subtitle_list = DecksControl.subtitles_list()
        layout = [[Text.CREATE_TITLE.create()],
                  [sg.Radio(Text.EMPTY_DECK.text,
                            group_id=0,
                            default=True,
                            key=Text.EMPTY_DECK.text,
                            enable_events=True),
                   sg.Radio(Text.AUTOFILL_DECK.text,
                            group_id=0,
                            key=Text.AUTOFILL_DECK.text,
                            enable_events=True)],
                  [Text.DECK_NAME.create(),
                   Inputbox.DECK_NAME.create()],
                  [Text.NEW_LIMIT.create(),
                   Inputbox.NEW_LIMIT.create()],
                  [Text.REVIEW_LIMIT.create(),
                   Inputbox.REVIEW_LIMIT.create()],
                  [Text.SOURCE.create(),
                   sg.Combo(subtitle_list, key=self._SUBTITLE_SOURCE, disabled=True)],
                  [Text.TARGET_COMP.create(),
                   Inputbox.TARGET_COMP.create()],
                  [sg.Text()],
                  [sg.Text(self._status, key=self._STATUS, size=(25, 2))],
                  [Button.CREATE_DECK.create()]]
        return layout

    def _window(self):
        window = sg.Window(self._NAME, layout=self._layout())
        return window

    def show(self):
        window = self._window()
        while True:
            event, values = window.Read()
            if event in [None, Button.BACK.text]:
                window.Close()
                break

            sections = {Button.CREATE_NEW_DECK.text: self._CREATE_WINDOW,
                        Button.ADD_CARDS.text: self._ADD_WINDOW,
                        Button.REMOVE_CARDS.text: self._REMOVE_WINDOW,
                        Button.DECK_STATS.text: self._STATS_WINDOW,
                        Button.DELETE_DECK.text: self._DELETE_WINDOW}
            if event in sections:
                for section in sections:
                    window.Element(sections[section]).update(visible=(section == event))

            if event in [Text.EMPTY_DECK.text, Text.AUTOFILL_DECK.text]:
                window.Element(self._SUBTITLE_SOURCE).update(disabled=(event == Text.EMPTY_DECK.text))

            if event == Button.CREATE_DECK.text:
                deck_list = DecksControl.deck_list()
                deck_name = values[Inputbox.DECK_NAME.key]

                if deck_name == '':
                    window.Element(self._STATUS).Update(self._BLANK_NAME)
                elif deck_name in deck_list:
                    window.Element(self._STATUS).Update(self._DECK_NAME_EXISTS)
                elif Text.AUTOFILL_DECK.text and values[self._SUBTITLE_SOURCE] == '':
                    window.Element(self._STATUS).Update(self._BLANK_SOURCE)
                else:
                    window.Element(self._STATUS).Update(self._DECK_CREATED)
                    # TODO: Create a deck


if __name__ == '__main__':
    DecksView().show()
