import PySimpleGUI as sg

from subscope.package.decks.decks_control import DecksControl
from subscope.package.decks.create_deck_view import CreateDeckView
from subscope.package.decks.add_cards_view import AddCardsView
from subscope.package.decks.delete_deck_view import DeleteDeckView
from subscope.package.decks.elements import Text, Button, InputBox


class DecksView:

    _NAME = 'Manage Decks'
    _DECK_NAME = 'DECK_NAME'
    _CREATE_WINDOW = 'CREATE'
    _ADD_WINDOW = 'ADD'
    _REMOVE_WINDOW = 'REMOVE'
    _STATS_WINDOW = 'STATS'
    _DELETE_WINDOW = 'DELETE'
    _NO_DECKS = '---Select A Deck---'

    def __init__(self):
        self._status = ''
        self._selected_deck = ''

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

        remove_window = [[sg.Text('Remove Cards')]]

        stats_window = [[sg.Text('Display Stats')]]

        window_height = 320
        layout = [[sg.Column(main_options, vertical_alignment='top'),
                   sg.VSeperator(),
                   sg.Column(CreateDeckView().layout(),
                             size=(400, window_height),
                             key=self._CREATE_WINDOW,
                             visible=True,
                             vertical_alignment='top'),
                   sg.Column(AddCardsView().layout(self._selected_deck),
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
                   sg.Column(DeleteDeckView().layout(self._selected_deck),
                             size=(400, window_height),
                             key=self._DELETE_WINDOW,
                             visible=False,
                             vertical_alignment='top')],
                  [sg.Column([[Button.BACK.create()]])]]
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

            self._selected_deck = values[self._DECK_NAME]
            CreateDeckView().events(event, values, window)
            AddCardsView().events(event, values, window, self._selected_deck)
            DeleteDeckView().events(event, values, window, self._selected_deck)


if __name__ == '__main__':
    DecksView().show()
