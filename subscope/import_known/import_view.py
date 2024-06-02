import PySimpleGUI as sg

from subscope.import_known.import_events import ImportEvents
from subscope.import_known.known_words_table import KnownWordsTable
from subscope.nav import Nav


class ImportView:
    _NAME = "Import Known Words"

    def __init__(self, state):
        self._local_state = state
        self._window = self._create_window()

    def _layout(self):
        print(self._local_state.known_words_table.headings)
        print(self._local_state.known_words_table.words)
        settings = [
            [
                sg.Text(
                    text="Import known words from a text file (e.g. exported Anki deck)"
                )
            ],
            [
                sg.Text(
                    text="Select the file to be imported (*.txt):",
                    size=(28, 1)
                ),
                sg.In(
                    default_text="",
                    size=(20, 1),
                    enable_events=True,
                    key=ImportEvents.BrowseFiles
                ),
                sg.FileBrowse(
                    file_types=(("Text Files (*.txt)", "*.txt"),)
                )
            ],
            [
                sg.Text(
                    text="Select the import column type:",
                    size=(28, 1)
                ),
                sg.Radio(
                    text="Word",
                    group_id=_RadioGroups.WORD_SENTENCE,
                    default=True,
                    key=_Keys.WORD
                ),
                sg.Radio(
                    text="Sentence",
                    group_id=_RadioGroups.WORD_SENTENCE,
                    key=_Keys.SENTENCE
                )
            ],
            [
                sg.Text(
                    text="Does the deck contain a header row?",
                    size=(28, 1)
                ),
                sg.Radio(
                    text="Yes",
                    group_id=_RadioGroups.HEADERS,
                    default=True,
                    key=_Keys.YES_HEADINGS
                ),
                sg.Radio(
                    text="No",
                    group_id=_RadioGroups.HEADERS,
                    key=_Keys.NO_HEADINGS
                )
            ],
            [
                sg.Text(
                    text="Select the target column:",
                    size=(28, 1)
                ),
                sg.Combo(
                    self._local_state.known_words_table.headings,
                    size=(15, 1),
                    key=_Keys.DECK_HEADINGS
                ),
                sg.Button(
                    button_text="Refresh List",
                    enable_events=True,
                    key=ImportEvents.FilterTable
                )
            ],
            [sg.Text('=' * 55)],
            [
                sg.Text(
                    text="Note:\n"
                         "- By default ALL words in the selected column will be marked as known.\n"
                         "- Sentences will be parsed to words. There is likely to be some \n"
                         "  inaccuracy in marked words.\n"
                         "- Words / sentences must not include furigana."
                )
            ],
            [sg.Text('=' * 55)],
            [
                sg.Button(
                    button_text="Back",
                    key=ImportEvents.Navigate(Nav.MAIN_MENU)
                ),
                sg.Button(
                    button_text="Import Known Words",
                    key=ImportEvents.ImportKnownWords
                )
            ]
        ]

        preview = [
            [
                sg.Text(
                    text="Word list preview:"
                )
            ],
            [
                sg.Table(
                    values=self._local_state.known_words_table.words,
                    headings=["1", "2", "3", "4", "5", "6", "7", "8"],
                    def_col_width=8,
                    auto_size_columns=False,
                    key=_Keys.PREVIEW,
                    size=(0, 18)
                )
            ]
        ]

        layout = [
            [
                sg.Column(
                    layout=settings
                ),
                sg.VSeperator(),
                sg.Column(
                    layout=preview,
                    vertical_alignment="top"
                )
            ]
        ]
        return layout

    def _create_window(self):
        window = sg.Window(
            title=self._NAME,
            layout=self._layout()
        )
        return window

    def show(self):
        # TODO mark words as known not yet implemented. Selecting headings yes/no doesn't do anything yet
        event, values = self._window.Read()
        if event is None:
            self.close()
            event = ImportEvents.Navigate(Nav.MAIN_MENU)

        elif event.name == ImportEvents.RefreshUI.name:
            self._refresh_ui()

        elif event.name == ImportEvents.BrowseFiles.name:
            input_file_path = values[ImportEvents.BrowseFiles]
            has_headings = values[_Keys.YES_HEADINGS]
            self._local_state.known_words_table = KnownWordsTable(input_file_path, has_headings)
            self.write_event(ImportEvents.RefreshUI)
            self.write_event(ImportEvents.FilterTable)
            self._update_state(self._local_state)

        elif event.name == ImportEvents.FilterTable.name:
            selected_column = values[_Keys.DECK_HEADINGS]
            column_contains_sentences = values[_Keys.SENTENCE]
            words = self._convert_words_table_to_display_words(selected_column, column_contains_sentences)
            display_words = [words[x:x+8] for x in range(0, len(words), 8)]
            self._window.Element(_Keys.PREVIEW).update(display_words)

        return event

    def write_event(self, event):
        self._window.write_event_value(event, None)

    def _refresh_ui(self):
        self._window.Element(_Keys.DECK_HEADINGS).update(
            self._local_state.known_words_table.headings[0],
            values=self._local_state.known_words_table.headings
        )
        self._window.Element(_Keys.PREVIEW).update(self._local_state.known_words_table.words)

    def _update_state(self, state):
        self._window.write_event_value(
            ImportEvents.UpdateState(
                state=state
            ),
            None
        )

    def _convert_words_table_to_display_words(self, selected_column, column_contains_sentences):
        words_column = []
        if selected_column != "":
            words_column = self._local_state.known_words_table.get_column_by_name(
                selected_column,
                column_contains_sentences
            )
        return words_column

    def close(self):
        self._window.close()


class _Keys:
    BROWSE = "-BROWSE-"
    WORD = "-WORD-"
    SENTENCE = "-SENTENCE-"
    YES_HEADINGS = "-YES_HEADINGS-"
    NO_HEADINGS = "-NO_HEADINGS-"
    DECK_HEADINGS = "-DECK_HEADINGS-"
    PREVIEW = "-PREVIEW-"


class _RadioGroups:
    WORD_SENTENCE = 1
    HEADERS = 2
