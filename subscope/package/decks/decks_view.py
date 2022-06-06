import PySimpleGUI as sg
from enum import Enum

from subscope.package.decks.decks_control import DecksControl
from subscope.package.Processing import CreateDeck as cd
from subscope.package.Processing import AddCards as ac
from subscope.package.Processing import RemoveCards as rc
from subscope.package.Processing import DeckStats as ds
from subscope.package.Processing import DeleteDeck as dd


class Text(Enum):

    MANAGE_DECKS = ('Manage Decks', 'any 14')
    DECK_LIST = ('Deck List', 'any 11')

    def __init__(self, text, font):
        self.text = text
        self.font = font

    def create(self):
        return sg.Text(self.text,
                       font=self.font)


class Button(Enum):

    CREATE_DECK = ('Create New Deck', False, cd.createUI, (16, 1))
    ADD_CARDS = ('Add Cards', True, ac.addUI, (16, 1))
    REMOVE_CARDS = ('Remove Cards', True, rc.removeUI, (16, 1))
    DECK_STATS = ('Deck Stats', True, ds.statsUI, (16, 1))
    DELETE_DECK = ('Delete Deck', True, dd.deleteUI, (16, 1))
    BACK = ('Back', False, None, None)

    def __init__(self, text, disabled, event, size):
        self.text = text
        self.disabled = disabled
        self.event = event
        if size is None:
            self.size = (None, None)
        else:
            self.size = size

    def create(self):
        button = sg.Button(self.text,
                           disabled=self.disabled,
                           size=self.size)
        return button


class DecksView:

    _NAME = 'Manage Decks'

    @property
    def _layout(self):
        headings = [[Text.MANAGE_DECKS.create()],
                    [Text.DECK_LIST.create()]]

        deck_list = [*[[sg.Radio(deck,
                                 group_id=1,
                                 enable_events=True,
                                 key=deck)]
                       for deck in DecksControl.deck_list()]]

        buttons = [[Button.CREATE_DECK.create()],
                   [Button.ADD_CARDS.create()],
                   [Button.REMOVE_CARDS.create()],
                   [Button.DECK_STATS.create()],
                   [Button.DELETE_DECK.create()]]

        layout = [[sg.Column(headings)],
                  [sg.Column(deck_list, size=(150, 190), scrollable=True),
                   sg.Column(buttons, vertical_alignment='top')],
                  [sg.Column([[Button.BACK.create()]])]]
        return layout

    @property
    def _window(self):
        window = sg.Window(self._NAME, layout=self._layout)
        return window

    def show(self):
        deck_name = ''
        window = self._window
        while True:
            event, values = window.Read()
            if event in [None, Button.BACK.text]:
                window.Close()
                break

            if event in DecksControl.deck_list():
                deck_name = event
                for button in Button:
                    window.Element(button.text).update(disabled=False)

            for button in Button:
                if event == button.text:
                    window.Hide()
                    button.event(deck_name)
                window.UnHide()
