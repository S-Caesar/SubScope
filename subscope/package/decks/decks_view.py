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
    DECK_NAME = ('Deck Name', None, (12, 1))
    NEW_LIMIT = ('New Limit', None, (12, 1))
    REVIEW_LIMIT = ('Review Limit', None, (12, 1))
    CARD_FORMAT = ('Card Format', None, (12, 1))
    SOURCE = ('Source', None, (12, 1))
    TARGET_COMP = 'Target Comprehension (%)'

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

    # Delete Window
    CONFIRM_DELETE_DECK = ('Confirm Deck Deletion', None)

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


class InputBox(Enum):

    DECK_NAME = ((14, 1), 'DECK_NAME_INPUT', '')
    NEW_LIMIT = ((5, 1), 'NEW_LIMIT_INPUT', 10)
    REVIEW_LIMIT = ((5, 1), 'REVIEW_LIMIT_INPUT', 50)
    TARGET_COMP = ((3, 1), 'TARGET_COMP_INPUT', 70, True)

    def __init__(self, size, key, default, disabled=False):
        self.size = size
        self.key = key
        self.default = default
        self.disabled = disabled

    def create(self):
        return sg.Input(default_text=self.default,
                        key=self.key,
                        size=self.size,
                        disabled=self.disabled)


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
    _FORMAT = 'FORMAT'
    _DECK_NAME_EXISTS = 'Deck name already exists'
    _DECK_CREATED = 'Deck created!'
    _BLANK_INPUT = 'Required input is blank:\n'
    _INVALID_INPUT = 'Input must be a number:\n'

    # Modify window
    _NO_DECKS = '---Select A Deck---'

    def __init__(self):
        self._status = ''

    def _layout(self):
        deck_list = DecksControl.deck_list()
        main_options = [[Text.TITLE.create()],
                        [Text.CREATE_DECK.create()],
                        [Button.CREATE_NEW_DECK.create()],
                        [sg.Text()],
                        [Text.MODIFY_DECK.create()],
                        [sg.Combo(deck_list,
                                  default_value=self._NO_DECKS,
                                  size=(17, 1),
                                  enable_events=True,
                                  key=self._DECK_NAME)],
                        [Button.ADD_CARDS.create()],
                        [Button.REMOVE_CARDS.create()],
                        [Button.DECK_STATS.create()],
                        [Button.DELETE_DECK.create()]]

        add_window = [[sg.Text('Add Cards to Deck')]]

        remove_window = [[sg.Text('Remove Cards')]]

        stats_window = [[sg.Text('Display Stats')]]

        delete_window = [[sg.Text('Delete Selected Deck?')],
                         [Button.CONFIRM_DELETE_DECK.create()]]

        window_height = 320
        layout = [[sg.Column(main_options, vertical_alignment='top'),
                   sg.VSeperator(),
                   sg.Column(self._create_window(),
                             size=(400, window_height),
                             key=self._CREATE_WINDOW,
                             visible=True,
                             vertical_alignment='top'),
                   sg.Column(add_window,
                             size=(400, window_height),
                             key=self._ADD_WINDOW,
                             visible=False,
                             vertical_alignment='top'),
                   sg.Column(remove_window,
                             size=(400, window_height),
                             key=self._REMOVE_WINDOW,
                             visible=False,
                             vertical_alignment='top'),
                   sg.Column(stats_window,
                             size=(400, window_height),
                             key=self._STATS_WINDOW,
                             visible=False,
                             vertical_alignment='top'),
                   sg.Column(delete_window,
                             size=(400, window_height),
                             key=self._DELETE_WINDOW,
                             visible=False,
                             vertical_alignment='top')],
                  [sg.Column([[Button.BACK.create()]])]]
        return layout

    def _create_window(self):
        format_list = DecksControl.formats_list()
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
                   InputBox.DECK_NAME.create()],
                  [Text.NEW_LIMIT.create(),
                   InputBox.NEW_LIMIT.create()],
                  [Text.REVIEW_LIMIT.create(),
                   InputBox.REVIEW_LIMIT.create()],
                  [Text.CARD_FORMAT.create(),
                   sg.Combo(format_list, key=self._FORMAT, default_value=format_list[0])],
                  [Text.SOURCE.create(),
                   sg.Combo(subtitle_list, key=self._SUBTITLE_SOURCE, disabled=True)],
                  [Text.TARGET_COMP.create(),
                   InputBox.TARGET_COMP.create()],
                  [sg.Text()],
                  [sg.Text(self._status, key=self._STATUS, size=(25, 2))],
                  [Button.CREATE_DECK.create()]]
        return layout

    def _window(self):
        window = sg.Window(self._NAME, layout=self._layout())
        return window

    def show(self):
        # TODO: add option to create a deck from multiple sources
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
                window.Element(InputBox.TARGET_COMP.key).update(disabled=(event == Text.EMPTY_DECK.text))

            if event == Button.CREATE_DECK.text:
                deck_list = DecksControl.deck_list()
                deck_name = values[InputBox.DECK_NAME.key]
                new_limit = values[InputBox.NEW_LIMIT.key]
                card_format = values[self._FORMAT]
                review_limit = values[InputBox.REVIEW_LIMIT.key]
                subtitle_source = values[self._SUBTITLE_SOURCE]
                target_comprehension = values[InputBox.TARGET_COMP.key]

                if deck_name == '':
                    window.Element(self._STATUS).Update(self._BLANK_INPUT + Text.DECK_NAME.text)
                elif deck_name in deck_list:
                    window.Element(self._STATUS).Update(self._DECK_NAME_EXISTS)
                elif new_limit == '':
                    window.Element(self._STATUS).Update(self._BLANK_INPUT + Text.NEW_LIMIT.text)
                elif review_limit == '':
                    window.Element(self._STATUS).Update(self._BLANK_INPUT + Text.REVIEW_LIMIT.text)
                elif values[Text.AUTOFILL_DECK.text] and subtitle_source == '':
                    window.Element(self._STATUS).Update(self._BLANK_INPUT + Text.SOURCE.text)
                elif values[Text.AUTOFILL_DECK.text] and target_comprehension == '':
                    window.Element(self._STATUS).Update(self._BLANK_INPUT + Text.TARGET_COMP.text)
                else:
                    try:
                        for item, error in [[new_limit, Text.NEW_LIMIT.text],
                                            [review_limit, Text.REVIEW_LIMIT.text]]:
                            try:
                                int(item)
                            except ValueError:
                                window.Element(self._STATUS).Update(self._INVALID_INPUT + error)
                                raise ValueError

                        if values[Text.AUTOFILL_DECK.text]:
                            try:
                                int(target_comprehension)
                            except ValueError:
                                window.Element(self._STATUS).Update(self._INVALID_INPUT + Text.TARGET_COMP.text)
                                raise ValueError

                        window.Element(self._STATUS).Update(self._DECK_CREATED)
                        if values[Text.EMPTY_DECK.text]:
                            subtitle_source = None
                            target_comprehension = None
                        DecksControl.create_deck(deck_name,
                                                 new_limit,
                                                 review_limit,
                                                 card_format,
                                                 subtitle_source,
                                                 target_comprehension)

                    except ValueError:
                        continue

            if event == Button.CONFIRM_DELETE_DECK.text:
                deck_name = values[self._DECK_NAME]
                if deck_name in DecksControl.deck_list():
                    DecksControl.delete_deck(values[self._DECK_NAME])
                else:
                    # TODO: Display this on the screen
                    print('Invalid deck!')


if __name__ == '__main__':
    DecksView().show()
