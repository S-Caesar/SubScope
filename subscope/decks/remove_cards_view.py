import PySimpleGUI as sg
import pandas as pd

from subscope.decks.decks_control import DecksControl
from subscope.decks.elements import Text, Button, Table


class RemoveCardsView:
    _SELECTED_DECK_REMOVE = 'SELECTED_DECK_REMOVE'
    # TODO: Properly integrate the headers, so they aren't manually typed in
    _HEADERS = ['Review State', 'Source', 'Analysed Output', 'Line Number', 'Word', 'Gloss', 'Sentence',
                'Audio Clip', 'Screenshot', 'Score', 'Last Review', 'Next Review', 'Status']

    def layout(self, selected_deck):
        try:
            deck = DecksControl.read_deck(selected_deck)
        except FileNotFoundError:
            deck = pd.DataFrame([['']*13], columns=self._HEADERS)

        heading = [[Text.REMOVE_TITLE.create()],
                   [sg.Text(selected_deck, key=self._SELECTED_DECK_REMOVE, size=(20, 1))],
                   [Text.SELECT_CARDS.create()]]

        card_list = [[Table.REMOVE_CARDS.create(deck)]]

        remove_cards = [[Button.REMOVE_CARDS.create()]]

        layout = [[sg.Column(heading)],
                  [sg.Column(card_list)],
                  [sg.Column(remove_cards)]]

        return layout

    def events(self, event, values, window, selected_deck):
        if selected_deck != '':
            window.Element(self._SELECTED_DECK_REMOVE).update(selected_deck)

            deck = DecksControl.read_deck(selected_deck)
            window.Element(Table.REMOVE_CARDS.key).update(values=deck.values.tolist())
