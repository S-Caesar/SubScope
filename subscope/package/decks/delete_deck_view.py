import PySimpleGUI as sg

from subscope.package.decks.decks_control import DecksControl
from subscope.package.decks.elements import Text, Button, InputBox


class DeleteDeckView:
    _SELECTED_DECK_DELETE = 'SELECTED_DECK_DELETE'
    _DELETE_STATUS = 'DELETE_STATUS'

    def __init__(self):
        self._delete_status = ''

    def layout(self, selected_deck):
        layout = [[Text.DELETE_TITLE.create()],
                  [Text.CONFIRM_DELETE.create()],
                  [sg.Text(selected_deck, key=self._SELECTED_DECK_DELETE, size=(20, 1))],
                  [sg.Text(self._delete_status, key=self._DELETE_STATUS, size=(25, 2))],
                  [Button.CONFIRM_DELETE_DECK.create()]]
        return layout

    def events(self, event, values, window, selected_deck):
        window.Element(self._SELECTED_DECK_DELETE).update(selected_deck)

        if event == Button.CONFIRM_DELETE_DECK.text:
            if selected_deck in DecksControl.deck_list():
                DecksControl.delete_deck(selected_deck)
                self._delete_status = Text.DECK_DELETED.text
                window.Element(self._DELETE_STATUS).update(self._delete_status)
            else:
                self._delete_status = Text.INVALID_DECK.text
                window.Element(self._DELETE_STATUS).update(self._delete_status)
