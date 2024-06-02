import PySimpleGUI as sg
from enum import Enum

from subscope.import_known.import_known_control import ImportKnownControl


class Text(Enum):

    GUIDANCE = ('Import known words from a text file (e.g. exported Anki deck)', None)
    SELECT_FILE = ('Select the file to be imported (*.txt):', (28, 1))
    SELECT_TYPE = ('Select the import column type:', (28, 1))
    SELECT_COLUMN = ('Select the target column:', (28, 1))
    HEADER_CHECK = ('Does the deck contain a header row?  ', None)
    NOTES = ('Note:\n'
             '- By default ALL words in the selected column will be marked as known.\n'
             '- Sentences will be parsed to words. There is likely to be some \n  '
             'inaccuracy in marked words.\n'
             '- Only a subset of parsed words will be display as this takes a long time.\n  '
             'when marking the words as learned, all sentences will be parsed.\n'
             '- Words / sentences must not include furigana.',
             None)
    PREVIEW = ('Word list preview:', None)

    def __init__(self, text, size):
        self.text = text
        self.size = size

    def create(self):
        if self.size is None:
            self.size = (None, None)
        text = sg.Text(self.text, size=self.size)
        return text


class Input(Enum):

    BROWSE = ('', (20, 1), True, '-PATH-')

    def __init__(self, default, size, events, key):
        self.default = default
        self.size = size
        self.events = events
        self.key = key

    def create(self):
        input_box = sg.In(default_text=self.default, size=self.size, enable_events=self.events, key=self.key)
        return input_box


class Button(Enum):

    REFRESH = ('Refresh List', True)
    BACK = ('Back', True)
    MARK_KNOWN = ('Mark Words As Known', True)

    def __init__(self, text, events):
        self.text = text
        self.events = events

    def create(self):
        button = sg.Button(self.text, enable_events=self.events)
        return button


class ImportKnownView:

    _NAME = 'Import Known Words'

    @staticmethod
    def _layout(deck_headings, table_headings, words):
        settings = [[Text.GUIDANCE.create()],
                    [Text.SELECT_FILE.create(),
                     Input.BROWSE.create(),
                     sg.FileBrowse(file_types=(('Text Files (*.txt)', '*.txt'),))],

                    [Text.SELECT_TYPE.create(),
                     sg.Radio('Word', 1, default=True, key='-WORD-'),
                     sg.Radio('Sentence', 1, key='-SENTENCE-')],

                    [Text.SELECT_COLUMN.create(),
                     sg.Combo(deck_headings, size=(15, 1), key='-HEADINGS-'),
                     Button.REFRESH.create()],

                    [Text.HEADER_CHECK.create(),
                     sg.Radio('Yes', 2, default=True, key='-H_YES-'),
                     sg.Radio('No', 2, key='-H_NO-')],

                    [sg.Text('=' * 55)],

                    [Text.NOTES.create()],

                    [sg.Text('=' * 55)],

                    [Button.BACK.create(),
                     Button.MARK_KNOWN.create()]]

        preview = [[Text.PREVIEW.create()],
                   [sg.Table([words],
                             headings=table_headings,
                             def_col_width=8,
                             auto_size_columns=False,
                             key='-PREVIEW-',
                             size=(0, 18))]]

        layout = [[sg.Column(settings),
                   sg.VSeperator(),
                   sg.Column(preview, vertical_alignment='t')]]

        return layout

    def _window(self, deck_headings, table_headings, words):
        window = sg.Window(self._NAME, self._layout(deck_headings, table_headings, words))
        return window

    def show(self):
        table_headings = ['1', '2', '3', '4', '5', '6', '7', '8']
        words = ['', '', '', '', '', '', '', '']
        deck_headings = ['']
        numbered_headings = ['']
        deck = []

        controller = ImportKnownControl()
        window = self._window(deck_headings, table_headings, words)
        while True:
            event, values = window.Read()
            if event in [None, 'Back']:
                window.Close()
                break

            if event == Input.BROWSE.key and values[Input.BROWSE.key]:
                deck = controller.get_deck(values[Input.BROWSE.key])
                deck_headings = deck[0:1][0]

                # Create numbered headings to ensure column names will be unique
                numbered_headings = []
                for idx, heading in enumerate(deck_headings):
                    numbered_headings.append(str(idx) + '. ' + heading)

                # Update the combo list and default value
                window.Element('-HEADINGS-').update(numbered_headings[0], values=numbered_headings)

            if event == Button.REFRESH.text:
                # Create the word list to be displayed based on user selected heading
                if values['-HEADINGS-'] or deck:
                    index = numbered_headings.index(values['-HEADINGS-'])
                    words = []
                    for idx, entry in enumerate(deck):
                        if idx == 0 and values['-H_YES-']:
                            continue
                        elif entry != ['']:
                            words.append(entry[index])

                # Sentences is selected, so parse a sample of the input first for the preview
                if not values['-WORD-']:
                    words = controller.parse_sentences(words, limit=10)
                display_words = [words[x:x+8] for x in range(0, len(words), 8)]
                window.Element('-PREVIEW-').update(display_words)

            if event == Button.MARK_KNOWN.text:
                if not values['-WORD-']:
                    words = controller.parse_sentences(words)
                controller.mark_known_words(words)


if __name__ == '__main__':
    ImportKnownView().show()
