import re

from subscope.analyse.ichiran import Ichiran


class KnownWordsTable:
    def __init__(self, input_file_path="", has_headings=False):
        self._input_file_path = input_file_path
        self._has_headings = has_headings

        self._raw_input = None
        self.words = None
        self.headings = None

        self._populate_table()

    def _populate_table(self):
        if self._input_file_path:
            self._raw_input = self._read_file()
            self._set_headings()
        else:
            placeholder = ["", "", "", "", "", "", "", ""]
            self.headings = placeholder
            self.words = placeholder

    def _read_file(self):
        if self._input_file_path:
            words = open(self._input_file_path).read().split("\n")
            for column, entry, in enumerate(words):
                words[column] = entry.split("\t")
            return words

    def _set_headings(self):
        if self._has_headings:
            headings = self._raw_input[0:1][0]
            # Create numbered headings to ensure column names will be unique
            for column, heading in enumerate(headings):
                headings[column] = f"{column + 1}. {heading}"
            self.headings = headings
            self.words = self._raw_input[1:]
        else:
            self.headings = list(range(1, len(self._raw_input[0:1][0])))
            self.words = self._raw_input

    def get_column_by_name(self, column_name, column_contains_sentences):
        column_number = self.headings.index(column_name)
        words_column = [row[column_number] for row in self.words]
        if column_contains_sentences:
            words_column = self._parse_sentences(words_column, limit=10)
        return words_column

    def _parse_sentences(self, sentences, limit=None):
        """Set a value for 'limit' to control the number of sentences to be parsed to avoid spending forever parsing"""
        word_list = []
        sentences = self._strip_text(sentences)
        for idx, sentence in enumerate(sentences):
            if limit and idx > limit:
                break
            else:
                print(sentence)
                word_list.extend(Ichiran().convert_line_to_table_rows(0, sentence, []))

        words = []
        for entry in word_list:
            words.append(entry[2])
        return words

    @staticmethod
    def _strip_text(input_lines):
        # TODO just copied this from 'parse_file', but would be better if it wasn't duplicated
        """Remove all non-Whitelisted characters from the input list of lists"""
        _WHITELIST = re.compile("[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]", re.UNICODE)

        output_lines = []
        for line in input_lines:
            line = re.sub(r"（.+?）", "", line)
            line = re.sub(r"\(.+?\)", "", line)
            line = [character for character in line if _WHITELIST.search(character)]
            output_lines.append(''.join(line))
        return output_lines
