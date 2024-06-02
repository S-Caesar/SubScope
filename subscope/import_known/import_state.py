from subscope.import_known.known_words_table import KnownWordsTable


class ImportState:
    def __init__(
            self, theme=None, known_words_table=None, display_words=None, table_has_headings=True
    ):
        self.theme = theme
        self.known_words_table = known_words_table or KnownWordsTable()
        self.display_words = display_words or []
        self.table_has_headings = table_has_headings
