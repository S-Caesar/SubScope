import PySimpleGUI as sg
from enum import Enum


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

    # Add Window
    ADD_TITLE = ('Add Cards', 'any 14')
    SORT_WORDS = 'Sort words by:'
    SEARCH_DATABASE = 'Search database:'
    SELECT_SOURCES = 'Select sources:'

    # Remove Window
    REMOVE_TITLE = ('Remove Cards', 'any 14')
    NO_CARDS = 'No cards in this deck'
    SELECT_CARDS = 'Select cards for removal'

    # Stats Window
    STATS_TITLE = ('Deck Stats', 'any 14')

    # Delete Window
    DELETE_TITLE = ('Delete Deck', 'any 14')
    CONFIRM_DELETE = 'Confirm deletion of selected deck?'
    DECK_DELETED = 'Deck deleted!'
    INVALID_DECK = 'Invalid deck selection'

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
    ADD_CARDS = ('Add Cards', (16, 1), True)
    REMOVE_CARDS = ('Remove Cards', (16, 1), True)
    DECK_STATS = ('Deck Stats', (16, 1), True)
    DELETE_DECK = ('Delete Deck', (16, 1), True)
    BACK = ('Back', None)

    # Create Window
    CREATE_DECK = ('Create Deck', None)

    # Add Window
    REFRESH = ('Refresh', None)
    ADD_TO_DECK = ('Add to Deck', None)

    # Remove Window
    REMOVE_SELECTED_CARDS = ('Remove Cards', None)

    # Delete Window
    CONFIRM_DELETE_DECK = ('Confirm Deck Deletion', None)

    def __init__(self, text, size, disabled=False):
        self.text = text
        if size is None:
            self.size = (None, None)
        else:
            self.size = size
        self.disabled = disabled

    def create(self):
        button = sg.Button(self.text,
                           size=self.size,
                           disabled=self.disabled)
        return button


class InputBox(Enum):

    # Create Window
    DECK_NAME = ((14, 1), 'DECK_NAME_INPUT', '')
    NEW_LIMIT = ((5, 1), 'NEW_LIMIT_INPUT', 10)
    REVIEW_LIMIT = ((5, 1), 'REVIEW_LIMIT_INPUT', 50)
    TARGET_COMP = ((3, 1), 'TARGET_COMP_INPUT', 70, True)

    # Add Window
    SEARCH_DATABASE = ((35, 0), 'SEARCH_DATABASE', '')

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


class Combo(Enum):

    # Add Window
    SORTING = (None, True, 'SORTING')

    def __init__(self, size, enable_events, key):
        if size is None:
            self.size = (None, None)
        else:
            self.size = size
        self.enable_events = enable_events
        self.key = key

    def create(self, options):
        return sg.Combo(options, size=self.size, enable_events=self.enable_events, key=self.key)


class Checkbox(Enum):

    # Add Window
    WORD_SOURCES = ('WORD_SOURCES', True, True)

    def __init__(self, key, enable_events, default):
        self.key = key
        self.enable_events = enable_events
        self.default = default

    def create(self, options):
        return [[sg.Checkbox(options[idx],
                             key=f'{self.key}_{idx}',
                             enable_events=self.enable_events,
                             default=self.default)]
                for idx, source in enumerate(options)]


class Table(Enum):

    # Add Window
    DATABASE = (11, True, 'DATABASE')
    REMOVE_CARDS = (12, True, 'REMOVE_CARDS')

    def __init__(self, num_rows, enable_events, key):
        self.num_rows = num_rows
        self.enable_events = enable_events
        self.key = key

    def create(self, dataframe):
        return sg.Table(values=dataframe.values.tolist(),
                        headings=dataframe.columns.tolist(),
                        key=self.key,
                        num_rows=self.num_rows,
                        enable_events=self.enable_events)
