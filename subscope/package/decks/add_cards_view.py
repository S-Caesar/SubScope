import PySimpleGUI as sg

from subscope.package.decks.decks_control import DecksControl
from subscope.package.decks.elements import Text, Button, InputBox, Combo, Checkbox, Table


class AddCardsView:
    _SELECTED_DECK_ADD = 'SELECTED_DECK_ADD'
    sort_options = ['Hiragana', 'Alphabet', 'Part of Speech', 'Frequency', 'Fewest Unknown']
    word_sources = DecksControl.subtitles_list()
    _READING = 'reading'
    _GLOSS = 'gloss'

    def __init__(self):
        self._database = DecksControl.get_word_data()
        self._all_words = self._database[self._READING].tolist()
        self._sub_database = self._database

    def layout(self, selected_deck):
        headings = [[Text.ADD_TITLE.create()],
                    [sg.Text(selected_deck, key=self._SELECTED_DECK_ADD, size=(20, 1))]]
        sorting = [[Text.SORT_WORDS.create(),
                    Combo.SORTING.create(self.sort_options),
                    Text.SEARCH_DATABASE.create(),
                    InputBox.SEARCH_DATABASE.create(),
                    Button.REFRESH.create()]]
        sources = [[Text.SELECT_SOURCES.create()],
                    *Checkbox.WORD_SOURCES.create(self.word_sources)]
        data_search = [[Table.DATABASE.create(self._database)],
                       [Button.ADD_TO_DECK.create()]]

        layout = [[sg.Column(headings)],
                  [sg.Column(sorting)],
                  [sg.Column(sources,
                             size=(150, 300),
                             scrollable=True,
                             vertical_scroll_only=True,
                             vertical_alignment='Top'),
                   sg.Column(data_search,
                             size=(600, 300))]]
        return layout

    def events(self, event, values, window, selected_deck):
        window.Element(self._SELECTED_DECK_ADD).update(selected_deck)

        selected_sources = {}
        for idx, source in enumerate(self.word_sources):
            if values[f'{Checkbox.WORD_SOURCES.key}_{idx}']:
                selected_sources[source] = True
            else:
                selected_sources[source] = False

        # TODO: Add option to search in Japanese as well
        # TODO: Sort the table out to show POS, definition, etc, in separate columns
        # TODO: Show / hide rows based on source selection
        # TODO: Tie in all the sort terms properly
        if event == Button.REFRESH.text:
            search = values[InputBox.SEARCH_DATABASE.key]
            self._sub_database = self._database[self._database[self._GLOSS].str.contains(search)]

            sort_by = {'': 'text',
                       'Hiragana': 'kana',
                       'Alphabet': 'gloss'}
            sort = values[Combo.SORTING.key]
            if sort in sort_by:
                self._sub_database.sort_values(by=[sort_by[sort]], inplace=True, ignore_index=True)

            self._all_words = self._sub_database[self._READING].tolist()
            window.Element(Table.DATABASE.key).update(values=self._sub_database.values.tolist())

        selected_rows = values[Table.DATABASE.key]
        words = []
        if event == Button.ADD_TO_DECK.text:
            for row_number in selected_rows:
                words.append(self._all_words[row_number])
            DecksControl.add_cards_to_deck(selected_deck, words)
