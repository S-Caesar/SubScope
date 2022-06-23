import PySimpleGUI as sg

from subscope.package.decks.decks_control import DecksControl
from subscope.package.decks.elements import Text, Button, InputBox


class AddCardsView:
    _SELECTED_DECK_ADD = 'SELECTED_DECK_ADD'

    def layout(self, selected_deck):
        layout = [[Text.ADD_TITLE.create()],
                  [sg.Text(selected_deck, key=self._SELECTED_DECK_ADD, size=(20, 1))]]
        return layout

    def events(self, event, values, window, selected_deck):
        window.Element(self._SELECTED_DECK_ADD).update(selected_deck)
