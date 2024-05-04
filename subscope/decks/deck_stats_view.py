import PySimpleGUI as sg

from subscope.decks.elements import Text


class DeckStatsView:
    _SELECTED_DECK_STATS = 'SELECTED_DECK_STATS'

    def layout(self, selected_deck):
        stats_window = [[Text.STATS_TITLE.create()],
                        [sg.Text(selected_deck, key=self._SELECTED_DECK_STATS, size=(20, 1))]]

        layout = [[sg.Column(stats_window)]]
        return layout
