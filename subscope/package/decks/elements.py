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
