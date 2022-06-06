class Word:

    def __init__(self):
        self.invalid = False
        self._line_no = None
        self._reading = None
        self._text = None
        self._kana = None
        self._score = None
        self._seq = None
        self._gloss = None
        self._conj_pos = None
        self._conj_type = None
        self._neg = None
        self._dict_reading = None
        self._dict_text = None
        self._dict_kana = None
        self._suffix = None

    def set_properties_with_ichiran_json(self, entry, line_no):
        self._line_no = line_no

        # First check whether the entry is a conjugation
        try:
            conjugation = entry['conj']
            if conjugation:
                conjugation = conjugation[0]
                self._conj_pos = conjugation['prop'][0]['pos']
                self._conj_type = conjugation['prop'][0]['type']
                try:
                    self._neg = conjugation['prop'][0]['neg']
                except KeyError:
                    pass

                try:
                    self._dict_reading = conjugation['reading']
                    self._gloss = conjugation['gloss']
                except KeyError:
                    # Conjugation is 'via' a previous conj. (e.g. Past form of Potential form)
                    if 'via' in conjugation:
                        via = conjugation['via'][0]
                        self._conj_pos = via['prop'][0]['pos'] + ' [via] ' + self._conj_pos
                        self._conj_type = via['prop'][0]['type'] + ' [via] ' + self._conj_type
                        self._dict_reading = via['reading']
                        self._gloss = via['gloss']
                    else:
                        self.invalid = True

                # Split up the dictionary entry into kanji and kana
                # If it is just kana, it will only have one string, so will be used for both
                dict_entry = self._dict_reading.split(' ')
                self._dict_text = dict_entry[0]
                if len(dict_entry) == 1:
                    self._dict_kana = dict_entry[0]
                else:
                    self._dict_kana = dict_entry[1].replace('【', '').replace('】', '')
        except KeyError:
            pass

        # If the entry is not a conjugation, the remaining fields should fill from the top level of the json
        # Some will error if the entry is a conj, but the property should have a value if that is the case
        try:
            self._reading = entry['reading']
        except KeyError:
            if self._reading is None:
                self.invalid = True

        try:
            self._text = entry['text']
        except KeyError:
            if self._text is None:
                self.invalid = True

        try:
            self._kana = entry['kana']
        except KeyError:
            if self._kana is None:
                self.invalid = True

        try:
            self._gloss = entry['gloss']
        except KeyError:
            if self._gloss is None:
                self.invalid = True

        try:
            self._score = entry['score']
        except KeyError:
            pass

        try:
            self._seq = entry['seq']
        except KeyError:
            pass

        try:
            self._suffix = entry['suffix']
        except KeyError:
            pass

    def set_properties_with_data_table_row(self):
        raise Exception('Not yet implemented')

    def get_list(self):
        word_info = [self._line_no, self._reading, self._text, self._kana, self._score, self._seq, self._gloss,
                     self._conj_pos, self._conj_type, self._neg, self._dict_reading, self._dict_text,
                     self._dict_kana, self._suffix]
        return word_info
