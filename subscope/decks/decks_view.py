import PySimpleGUI as sg

from subscope.decks.decks_control import DecksControl
from subscope.decks.create_deck_view import CreateDeckView
from subscope.decks.add_cards_view import AddCardsView
from subscope.decks.remove_cards_view import RemoveCardsView
from subscope.decks.deck_stats_view import DeckStatsView
from subscope.decks.delete_deck_view import DeleteDeckView
from subscope.decks.elements import Text, Button


class DecksView:
    _NAME = 'Manage Decks'
    _DECK_NAME = 'DECK_NAME'
    _CREATE_WINDOW = 'CREATE'
    _ADD_WINDOW = 'ADD'
    _REMOVE_WINDOW = 'REMOVE'
    _STATS_WINDOW = 'STATS'
    _DELETE_WINDOW = 'DELETE'

    def __init__(self):
        self._status = ''
        self._selected_deck = ''

    def _layout(self, create_deck, add_cards, remove_cards, deck_stats, delete_deck):
        deck_list = DecksControl.deck_list()
        main_options = [[Text.TITLE.create()],
                        [Text.CREATE_DECK.create()],
                        [Button.CREATE_NEW_DECK.create()],
                        [sg.Text()],
                        [Text.MODIFY_DECK.create()],
                        [sg.Combo(deck_list,
                                  default_value='',
                                  size=(17, 1),
                                  enable_events=True,
                                  key=self._DECK_NAME)],
                        [Button.ADD_CARDS.create()],
                        [Button.REMOVE_CARDS.create()],
                        [Button.DECK_STATS.create()],
                        [Button.DELETE_DECK.create()],
                        [sg.Text()],
                        [Button.BACK.create()]]

        window_width = 800
        window_height = 350
        layout = [sg.Column(main_options, vertical_alignment='top')]
        layout.extend([sg.VSeperator(),
                       sg.Column(create_deck.layout(),
                                 size=(window_width, window_height),
                                 key=self._CREATE_WINDOW,
                                 visible=True,
                                 vertical_alignment='top')])
        layout.extend([sg.Column(add_cards.layout(self._selected_deck),
                                 size=(window_width, window_height),
                                 key=self._ADD_WINDOW,
                                 visible=False,
                                 vertical_alignment='top')])
        layout.extend([sg.Column(remove_cards.layout(self._selected_deck),
                                 size=(window_width, window_height),
                                 key=self._REMOVE_WINDOW,
                                 visible=False,
                                 vertical_alignment='top'),
                       sg.Column(deck_stats.layout(self._selected_deck),
                                 size=(window_width, window_height),
                                 key=self._STATS_WINDOW,
                                 visible=False,
                                 vertical_alignment='top'),
                       sg.Column(delete_deck.layout(self._selected_deck),
                                 size=(window_width, window_height),
                                 key=self._DELETE_WINDOW,
                                 visible=False,
                                 vertical_alignment='top')])

        return [layout]

    def _window(self, create_deck, add_cards, remove_cards, deck_stats, delete_deck):
        window = sg.Window(self._NAME,
                           layout=self._layout(create_deck, add_cards, remove_cards, deck_stats, delete_deck))
        return window

    def show(self):
        # TODO: add option to create a deck from multiple sources
        create_deck = CreateDeckView()
        add_cards = AddCardsView()
        remove_cards = RemoveCardsView()
        deck_stats = DeckStatsView()
        delete_deck = DeleteDeckView()
        deck_buttons = [Button.ADD_CARDS.text, Button.REMOVE_CARDS.text, Button.DECK_STATS.text, Button.DELETE_DECK.text]
        window = self._window(create_deck, add_cards, remove_cards, deck_stats, delete_deck)
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

            created = create_deck.events(event, values, window)
            if created:
                self._update_deck_list(window)

            self._selected_deck = values[self._DECK_NAME]
            if self._selected_deck == '':
                for button in deck_buttons:
                    window.Element(button).update(disabled=True)
            else:
                for button in deck_buttons:
                    window.Element(button).update(disabled=False)

                add_cards.events(event, values, window, self._selected_deck)
                remove_cards.events(event, values, window, self._selected_deck)
                deleted = delete_deck.events(event, values, window, self._selected_deck)
                if deleted:
                    deck_list = DecksControl.deck_list()
                    if len(deck_list) == 0:
                        self._selected_deck = ''
                        window.write_event_value(Button.CREATE_NEW_DECK.text,'')
                    else:
                        self._selected_deck = DecksControl.deck_list()[0]
                    self._update_deck_list(window)

    def _update_deck_list(self, window):
        # Need to set the selected deck again after updating the list, otherwise it resets to blank
        window.Element(self._DECK_NAME).update(values=DecksControl.deck_list())
        window.Element(self._DECK_NAME).update(self._selected_deck)


if __name__ == '__main__':
    DecksView().show()
