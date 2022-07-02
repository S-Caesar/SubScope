import PySimpleGUI as sg
from enum import Enum
import ast
import datetime

import pandas as pd

from subscope.package.review.review_control import ReviewControl
from subscope.package.options.options import Options


class Text(Enum):
    SELECT_DECK = 'Select deck to review'
    CLICK_WORD = ('Click on a word in the example sentence to display glossary information below', None, None, (25, 3))

    # Card Details
    WORD = ('', 'WORD', 'any 18', (41, 1), 'c', 'black')
    PART = ('', 'PART', 'any 12', (53, 1), 'c', 'black')
    DEFINITION = ('', 'DEFINITION', 'any 16', (39, 2), 'c', 'black')
    INFO = ('', 'INFO', 'any 12', (43, 2), 'c', 'black')
    GLOSS_WORD = ('', 'GLOSS_WORD', 'any 16', (18, 2))
    GLOSSARY = ('', 'GLOSSARY', 'any 12', (21, 40))

    def __init__(self, text, key=None, font=None, size=None, justification=None, background_colour=None,
                 text_colour='white'):
        self.text = text
        self.key = key
        self.font = font
        if size is None:
            self.size = (None, None)
        else:
            self.size = size
        self.justification = justification
        self.background_colour = background_colour
        self.text_colour = text_colour

    def create(self):
        return sg.Text(self.text,
                       key=self.key,
                       font=self.font,
                       size=self.size,
                       justification=self.justification,
                       background_color=self.background_colour,
                       text_color=self.text_colour)


class Button(Enum):
    FLIP = ('Flip', 'grey99', 'grey30', '', (10, 2))
    AGAIN = ('Again', 'grey99', 'red2', 0, (10, 2))
    HARD = ('Hard', 'grey99', 'dark orange', 1, (10, 2))
    GOOD = ('Good', 'grey99', 'green3', 2, (10, 2))
    EASY = ('Easy', 'grey99', 'DeepSkyBlue3', 3, (10, 2))
    AUDIO = ('Audio', None, None, None, (10, 2))
    KNOWN = ('Known', None, None, None, (10, 1))
    SUSPEND = ('Suspend', None, None, None, (10, 1))
    BACK = ('Back', None, None, None, None, False)

    def __init__(self, text, text_colour=None, button_colour=None, response_score=None, size=None,
                 disabled=True):
        self.text = text
        self.text_colour = text_colour
        self.button_colour = button_colour
        self.response_score = response_score
        if size is None:
            self.size = (None, None)
        else:
            self.size = size
        self.disabled = disabled

    def create(self):
        return sg.Button(self.text,
                         size=self.size,
                         disabled=self.disabled,
                         button_color=(self.text_colour, self.button_colour))


class ReviewView:
    _REVIEW_TITLE = 'Review Decks'
    _DECK_LIST = ReviewControl.deck_list()
    _SELECTED_DECK = 'SELECTED_DECK'
    _IMAGE = 'IMAGE'
    _REVIEWS_FINISHED = 'Reviews Finished!'
    _card_front = False
    _REVIEW = 'Review'
    _KNOWN = 'Known'
    _SUSPENDED = 'Suspended'

    _SENTENCE_ONE = 'SENTENCE_ONE'
    _SENTENCE_TWO = 'SENTENCE_TWO'

    _WORD = 'Word'
    _READING = 'reading'
    _TEXT = 'text'
    _DICT_TEXT = 'dict_text'
    _CARD_PART = 'pos'
    _GLOSS = 'Gloss'
    _CARD_GLOSS = 'gloss'
    _CARD_INFO = 'info'
    _SENTENCE = 'Sentence'
    _AUDIO = 'Audio Clip'
    _SCREENSHOT = 'Screenshot'
    _SCORE = 'Score'
    _SOURCE = 'Source'
    _EPISODE = 'Analysed Output'
    _LINE_NUMBER = 'Line Number'
    _STATE = 'Review State'
    _LAST_REVIEW = 'Last Review'
    _NEXT_REVIEW = 'Next Review'
    _STATUS = 'Status'
    _SUFFIX = 'suffix'
    _NO_ENTRY = 'No Entry'

    # I use this character in place of string apostrophes when dealing with the Ichiran output
    _SUBSTITUTE = '^'
    _APOSTROPHE = '\''

    _active_deck = None
    _sentence_data_one = pd.DataFrame([])
    _sentence_data_two = pd.DataFrame([])

    _PART_COLOURING = {'n': 'green4',
                       'pn': 'DarkOrange1',
                       'prt': 'purple3',
                       'adv': 'red3',
                       'adj': 'deep sky blue',
                       'v': 'DarkGoldenrod4',
                       'int': 'gray',
                       'cop': 'maroon3',
                       'suf': 'medium blue',
                       'conj': 'OliveDrab4',
                       'exp': 'NavajoWhite'}
    _VERB_TYPES = ['v1', 'v5r', 'v5t', 'v5r-i', 'v5u', 'v5s', 'v5n', 'v5k-s', 'vi', 'vt', 'vs', 'vs-i', 'vk', 'aux-v']
    _VERB = 'v'
    _ADJECTIVE_TYPES = ['adj-no', 'adj-pn', 'adj-i', 'adj-na', 'adj-f']
    _ADJECTIVE = 'adj'
    _BLACK = 'black'
    _WHITE = 'white'

    @classmethod
    def _layout(cls):
        select = [[Text.SELECT_DECK.create()],
                  [sg.Combo(cls._DECK_LIST, key=cls._SELECTED_DECK, size=(15, 1), enable_events=True, readonly=True)]]

        card = [[Text.WORD.create()],
                [Text.PART.create()],
                [Text.DEFINITION.create()],
                [Text.INFO.create()],
                *[[sg.Text(text,
                           enable_events=True,
                           font='bold 18',
                           key=f'{cls._SENTENCE_ONE}{index}',
                           background_color=cls._BLACK)
                   for index, text in enumerate([''] * 10)]],
                *[[sg.Text(text,
                           enable_events=True,
                           font='bold 18',
                           key=f'{cls._SENTENCE_TWO}{index}',
                           background_color=cls._BLACK)
                   for index, text in enumerate([''] * 10)]],
                [sg.Image(key=cls._IMAGE, visible=True, background_color=cls._BLACK)]]

        button_row = []
        response_buttons = [Button.FLIP, Button.AGAIN, Button.HARD, Button.GOOD, Button.EASY]
        for button in response_buttons:
            button_row.append(button.create())
        card.extend([button_row,
                     [Button.AUDIO.create()],
                     [Button.KNOWN.create(), Button.SUSPEND.create()]])

        glossary = [[Text.CLICK_WORD.create()],
                    [sg.Text('_' * 27)],
                    [Text.GLOSS_WORD.create()],
                    [Text.GLOSSARY.create()]]

        back_button = [[Button.BACK.create()]]

        window_height = 650
        layout = [[sg.Column(select, size=(150, window_height), vertical_alignment='top'),
                   sg.VSeparator(),
                   sg.Column(card, size=(591, window_height), element_justification='c', background_color=cls._BLACK),
                   sg.VSeparator(),
                   sg.Column(glossary, size=(200, window_height))],
                  [sg.Column(back_button)]]
        return layout

    @classmethod
    def _window(cls):
        return sg.Window(cls._REVIEW_TITLE, layout=cls._layout(), return_keyboard_events=True)

    @classmethod
    def show(cls):
        window = cls._window()
        deck = None
        card = None
        index = None
        audio = None
        response_buttons = {Button.AGAIN: '1',
                            Button.HARD: '2',
                            Button.GOOD: '3',
                            Button.EASY: '4'}
        while True:
            event, values = window.read()
            if event in [None, 'Back']:
                try:
                    audio.terminate()
                except AttributeError:
                    pass
                window.close()
                break

            try:
                if values[event] in ReviewControl.deck_list():
                    cls._active_deck = values[event]
                    deck = ReviewControl.load_deck(cls._active_deck)
                    if len(deck.index.tolist()) == 0:
                        cls._set_state_finished(window, response_buttons)
                    else:
                        audio, card, index = cls._next_card(window, deck, audio, response_buttons)

                        window.Element(Button.AUDIO.text).update(disabled=False)
                        window.Element(Button.KNOWN.text).update(disabled=False)
                        window.Element(Button.SUSPEND.text).update(disabled=False)
            except KeyError:
                pass

            if event == Button.FLIP.text:
                cls._set_state_back(window, card, response_buttons)

            if event == Button.AUDIO.text:
                audio.terminate()
                audio = ReviewControl.play_audio(card[cls._SOURCE], card[cls._AUDIO])

            if event == Button.KNOWN.text:
                deck.loc[index, cls._STATE] = 1
                deck.loc[index, cls._STATUS] = cls._KNOWN
                audio, card, index = cls._next_card(window, deck, audio, response_buttons)

            if event == Button.SUSPEND.text:
                deck.loc[index, cls._STATE] = 1
                deck.loc[index, cls._STATUS] = cls._SUSPENDED
                audio, card, index = cls._next_card(window, deck, audio, response_buttons)

            if not cls._card_front:
                for button in response_buttons:
                    if event == button.text or event == response_buttons[button]:
                        deck = cls._record_response(deck, index, button.response_score)
                        deck = cls._update_review_dates(deck, index, button.response_score)
                        audio, card, index = cls._next_card(window, deck, audio, response_buttons)

            if cls._SENTENCE_ONE in event:
                clicked_word = window.Element(event).get()
                if clicked_word != '':
                    entry = cls._sentence_data_one[cls._sentence_data_one[cls._TEXT] == clicked_word]
                    reading = entry[cls._READING].tolist()[0]
                    gloss = entry[cls._CARD_GLOSS].tolist()[0]
                    gloss = cls._format_json_glossary(gloss)
                    if gloss == cls._NO_ENTRY:
                        gloss = str(entry[cls._SUFFIX].to_list()[0])
                    window.Element(Text.GLOSS_WORD.key).update(reading)
                    window.Element(Text.GLOSSARY.key).update(gloss)

            if cls._SENTENCE_TWO in event:
                clicked_word = window.Element(event).get()
                if clicked_word != '':
                    entry = cls._sentence_data_two[cls._sentence_data_two[cls._TEXT] == clicked_word]
                    reading = entry[cls._READING].tolist()[0]
                    gloss = entry[cls._CARD_GLOSS].tolist()[0]
                    gloss = cls._format_json_glossary(gloss)
                    window.Element(Text.GLOSS_WORD.key).update(reading)
                    window.Element(Text.GLOSSARY.key).update(gloss)

    @classmethod
    def _next_card(cls, window, deck, audio, response_buttons):
        if audio is not None:
            audio.terminate()

        try:
            card, index = cls._load_card(deck)
            audio = cls._set_state_front(window, card, response_buttons)
        except IndexError:
            card = None
            index = None
            cls._set_state_finished(window, response_buttons)
            cls._update_deck(deck)

        return audio, card, index

    @classmethod
    def _load_card(cls, deck):
        cards = deck[deck[cls._STATE] == 0]
        index = cards.index.tolist()[0]
        card = cards.iloc[0]
        return card, index

    @classmethod
    def _set_state_front(cls, window, card, response_buttons):
        cls._card_front = True

        window.Element(Button.FLIP.text).update(disabled=False)
        for button in response_buttons:
            window.Element(button.text).update(disabled=True)

        gloss = cls._split_glossary(card)
        part = gloss[cls._CARD_PART]
        window.Element(Text.WORD.key).update(card[cls._WORD])
        window.Element(Text.PART.key).update(part)
        window.Element(Text.DEFINITION.key).update('')
        window.Element(Text.INFO.key).update('')

        source = card[cls._SOURCE]
        episode = card[cls._EPISODE]
        line_number = card[cls._LINE_NUMBER]
        sentences = ReviewControl.get_sentences(source, episode, line_number)

        sentence_data = ReviewControl.get_sentence_data(source, episode, line_number)
        for index, data in enumerate(sentence_data):
            if len(data) != 0 and cls._TEXT in data.columns.tolist():
                sentence_data[index] = cls._order_sentences(sentences[index], data)

        try:
            cls._sentence_data_one = sentence_data[0]
        except IndexError:
            cls._sentence_data_one = pd.DataFrame([])

        try:
            cls._sentence_data_two = sentence_data[1]
        except IndexError:
            cls._sentence_data_two = pd.DataFrame([])

        cls._update_sentence_text(window, sentence_data)

        screenshot = card[cls._SCREENSHOT]
        screenshot = ReviewControl.load_screenshot(source, screenshot)
        window.Element(cls._IMAGE).Update(screenshot.getvalue())

        audio_file = card[cls._AUDIO]
        audio = ReviewControl.play_audio(source, audio_file)

        window.Element(Button.FLIP.text).update(disabled=False)
        return audio

    @classmethod
    def _order_sentences(cls, sentence, sentence_data):
        ordered_sentence = []
        word_list = sentence_data[cls._TEXT].tolist()
        while len(sentence) > 0:
            added = False
            for index, word in enumerate(word_list):
                if word[:len(word)] == sentence[:len(word)]:
                    ordered_sentence.append(word)
                    sentence = sentence[len(word):]
                    del word_list[index]
                    added = True
                    break

            if not added:
                if len(sentence) > 1:
                    ordered_sentence.append(sentence[0])
                    sentence = sentence[1:]
                elif len(sentence) == 1:
                    ordered_sentence.append(sentence[0])
                    break

        for word in ordered_sentence:
            target_index = sentence_data[(sentence_data[cls._TEXT] == word)].index.tolist()
            if len(target_index) != 0:
                if len(target_index) > 1:
                    target_index = [target_index[0]]
                index = sentence_data.index.tolist()
                index.pop(target_index[0])
                sentence_data = sentence_data.reindex(index + target_index)
                sentence_data = sentence_data.reset_index(drop=True)
            else:
                sentence_data = pd.concat([sentence_data, pd.DataFrame([word], columns=[cls._TEXT])])
                sentence_data = sentence_data.reset_index(drop=True)

        return sentence_data.fillna(cls._NO_ENTRY)

    @classmethod
    def _update_sentence_text(cls, window, sentence_data):
        blanks = [''] * 10
        for index, blank in enumerate(blanks):
            window.Element(f'{cls._SENTENCE_ONE}{index}').update(blank)
            window.Element(f'{cls._SENTENCE_ONE}{index}').update(text_color=cls._WHITE)
            window.Element(f'{cls._SENTENCE_TWO}{index}').update(blank)
            window.Element(f'{cls._SENTENCE_TWO}{index}').update(text_color=cls._WHITE)

        try:
            words = sentence_data[0][cls._TEXT].tolist()
            if len(words) > 0:
                for index, word in enumerate(words):
                    window.Element(f'{cls._SENTENCE_ONE}{index}').update(word)

                    gloss_json = sentence_data[0][cls._CARD_GLOSS][index]
                    text_colour = cls._text_colour_for_part_of_speech(gloss_json)
                    window.Element(f'{cls._SENTENCE_ONE}{index}').update(text_color=text_colour)
        except KeyError:
            pass

        if len(sentence_data) == 2:
            try:
                words = sentence_data[1][cls._TEXT].tolist()
                if len(words) > 0:
                    for index, word in enumerate(words):
                        window.Element(f'{cls._SENTENCE_TWO}{index}').update(word)

                        gloss_json = sentence_data[1][cls._CARD_GLOSS][index]
                        text_colour = cls._text_colour_for_part_of_speech(gloss_json)
                        window.Element(f'{cls._SENTENCE_TWO}{index}').update(text_color=text_colour)
            except KeyError:
                pass

    @classmethod
    def _text_colour_for_part_of_speech(cls, gloss_json):
        text_colour = cls._WHITE
        if Options.srs_colouring() == 'On':
            if gloss_json != cls._NO_ENTRY:
                gloss = ast.literal_eval(gloss_json)
                if cls._CARD_PART in gloss:
                    gloss = [gloss]

                part_of_speech = gloss[0][cls._CARD_PART].replace('[', '').replace(']', '')
                if ',' in part_of_speech:
                    part_of_speech = part_of_speech.split(',')[0]

                if part_of_speech in cls._VERB_TYPES:
                    part_of_speech = cls._VERB
                elif part_of_speech in cls._ADJECTIVE_TYPES:
                    part_of_speech = cls._ADJECTIVE

                if part_of_speech in cls._PART_COLOURING:
                    text_colour = cls._PART_COLOURING[part_of_speech]
                else:
                    print(part_of_speech)
        return text_colour

    @classmethod
    def _set_state_back(cls, window, card, response_buttons):
        cls._card_front = False

        gloss = cls._split_glossary(card)
        card_gloss = gloss[cls._CARD_GLOSS].replace(cls._SUBSTITUTE, cls._APOSTROPHE)
        info = gloss[cls._CARD_INFO]
        window.Element(Text.DEFINITION.key).update(card_gloss)
        window.Element(Text.INFO.key).update(info)

        window.Element(Button.FLIP.text).update(disabled=True)
        for button in response_buttons:
            window.Element(button.text).update(disabled=False)

    @classmethod
    def _split_glossary(cls, card):
        gloss = card[cls._GLOSS]
        gloss = ast.literal_eval(gloss[1:-1])
        # TODO: Provide all definitions, instead of just one - maybe with arrow buttons to change display
        if cls._CARD_PART not in gloss:
            gloss = gloss[0]

        for item in [cls._CARD_PART, cls._CARD_GLOSS, cls._CARD_INFO]:
            if item not in gloss:
                gloss[item] = ''
        return gloss

    @classmethod
    def _format_json_glossary(cls, gloss):
        if cls._NO_ENTRY not in gloss:
            gloss = ast.literal_eval(gloss[1:-1])
            if cls._CARD_PART in gloss:
                gloss = [gloss]

            str_gloss = ''
            for definition in gloss:
                if definition != cls._NO_ENTRY:
                    str_gloss += definition[cls._CARD_PART] + '\n' + definition[cls._CARD_GLOSS] + '\n\n'

            str_gloss = str_gloss.replace(cls._SUBSTITUTE, cls._APOSTROPHE)
        else:
            str_gloss = cls._NO_ENTRY
        return str_gloss

    @classmethod
    def _record_response(cls, deck, index, response_score):
        deck.loc[index, cls._STATE] = 1

        current_score = deck[cls._SCORE][index]
        deck.loc[index, cls._SCORE] = cls._adjust_score(response_score, current_score)
        return deck

    @staticmethod
    def _adjust_score(response_score, current_score):
        updated_score = round(current_score + (0.1 - (3 - response_score) * (0.1 + (3 - response_score) * 0.06)), 3)
        if updated_score < 1.3:
            updated_score = 1.3
        return updated_score

    @classmethod
    def _update_review_dates(cls, deck, index, response_score):
        if str(deck[cls._LAST_REVIEW][index]) == '0':
            interval = 1
        else:
            next_review = datetime.datetime.strptime(str(deck.loc[index, cls._NEXT_REVIEW]), '%Y-%m-%d')
            last_review = datetime.datetime.strptime(str(deck.loc[index, cls._LAST_REVIEW]), '%Y-%m-%d')
            interval = next_review - last_review
            if interval.days < 1:
                interval = 1
            else:
                interval = interval.days

        if response_score == 0:
            new_interval = 1
        else:
            new_interval = round(interval * deck[cls._SCORE][index])

        deck.loc[index, cls._LAST_REVIEW] = datetime.date.today()
        deck.loc[index, cls._NEXT_REVIEW] = deck.loc[index, cls._LAST_REVIEW] + datetime.timedelta(days=new_interval)
        deck.loc[index, cls._STATUS] = cls._REVIEW
        return deck

    @classmethod
    def _set_state_finished(cls, window, response_buttons):
        cls._card_front = True
        window.Element(Text.WORD.key).update(cls._REVIEWS_FINISHED)
        window.Element(Text.PART.key).update('')
        window.Element(Text.DEFINITION.key).update('')
        window.Element(Text.INFO.key).update('')
        window.Element(Text.GLOSS_WORD.key).update('')
        window.Element(Text.GLOSSARY.key).update('')
        window.Element(cls._IMAGE).Update(None)
        for button in response_buttons:
            window.Element(button.text).update(disabled=True)
        window.Element(Button.AUDIO.text).update(disabled=True)
        window.Element(Button.KNOWN.text).update(disabled=True)
        window.Element(Button.SUSPEND.text).update(disabled=True)

        blanks = [''] * 10
        for index, blank in enumerate(blanks):
            window.Element(f'{cls._SENTENCE_ONE}{index}').update(blank)
            window.Element(f'{cls._SENTENCE_TWO}{index}').update(blank)

    @classmethod
    def _update_deck(cls, deck):
        for index in deck.index.tolist():
            deck.loc[index, cls._STATE] = 0
        ReviewControl.update_deck(deck, cls._active_deck)


if __name__ == '__main__':
    ReviewView.show()
