import PySimpleGUI as sg
import ast
import datetime
import pandas as pd

from subscope.package.review.review_control import ReviewControl
from subscope.package.options.options import Options
from subscope.package.parsing.elements import Text, IterText, Button, Image


class ReviewView:
    _window = None
    _controller = None

    _REVIEW_TITLE = 'Review Decks'
    _DECK_LIST = ReviewControl.deck_list()
    _SELECTED_DECK = 'SELECTED_DECK'
    _REVIEWS_FINISHED = 'Reviews Finished!'
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
    _card_front = False
    _sentence_data = [pd.DataFrame([]), pd.DataFrame([])]

    _RESPONSE_BUTTONS = {Button.AGAIN: '1',
                         Button.HARD: '2',
                         Button.GOOD: '3',
                         Button.EASY: '4'}
    _AUX_BUTTONS = [Button.AUDIO, Button.KNOWN, Button.SUSPEND]

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
    def _create_layout(cls):
        select = [[Text.SELECT_DECK.create()],
                  [sg.Combo(cls._DECK_LIST, key=cls._SELECTED_DECK, size=(15, 1), enable_events=True, readonly=True)]]

        card = [[Text.WORD.create()],
                [Text.PART.create()],
                [Text.DEFINITION.create()],
                [Text.INFO.create()],
                *IterText.SENTENCE_ONE.create(),
                *IterText.SENTENCE_TWO.create(),
                [Image.CARD.create()]]

        button_row = []
        for button in [Button.FLIP] + list(cls._RESPONSE_BUTTONS.keys()):
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
    def _create_window(cls):
        return sg.Window(cls._REVIEW_TITLE, layout=cls._create_layout(), return_keyboard_events=True)

    @classmethod
    def show(cls):
        cls._window = cls._create_window()
        cls._controller = ReviewControl()
        deck = None
        card = None
        index = None

        while True:
            event, values = cls._window.read()
            if event in [None, 'Back']:
                cls._controller.stop_audio()
                cls._window.close()
                break

            try:
                if values[event] in cls._controller.deck_list():
                    deck = cls._controller.load_deck(values[event])
                    if cls._controller.remaining_cards() == 0:
                        cls._set_state_finished()
                    else:
                        card, index = cls._next_card(deck)

                        for button in cls._AUX_BUTTONS:
                            button.enable(cls._window)
            except KeyError:
                pass

            if event == Button.FLIP.text:
                cls._set_state_back(card)

            if event == Button.AUDIO.text:
                cls._controller.play_audio(card[cls._SOURCE], card[cls._AUDIO])

            if event == Button.KNOWN.text:
                deck.loc[index, cls._STATE] = 1
                deck.loc[index, cls._STATUS] = cls._KNOWN
                card, index = cls._next_card(deck)

            if event == Button.SUSPEND.text:
                deck.loc[index, cls._STATE] = 1
                deck.loc[index, cls._STATUS] = cls._SUSPENDED
                card, index = cls._next_card(deck)

            if not cls._card_front:
                for button in cls._RESPONSE_BUTTONS:
                    if event == button.text or event == cls._RESPONSE_BUTTONS[button]:
                        deck = cls._record_response(deck, index, button.response_score)
                        deck = cls._update_review_dates(deck, index, button.response_score)
                        card, index = cls._next_card(deck)

            for sentence_index, sentence in enumerate([IterText.SENTENCE_ONE, IterText.SENTENCE_TWO]):
                if sentence.key in event:
                    clicked_word = cls._window.Element(event).get()
                    if clicked_word != '':
                        sentence_data = cls._sentence_data[sentence_index]
                        entry = sentence_data[sentence_data[cls._TEXT] == clicked_word]
                        reading = entry[cls._READING].tolist()[0]
                        gloss = entry[cls._CARD_GLOSS].tolist()[0]
                        gloss = cls._format_json_glossary(gloss)
                        if gloss == cls._NO_ENTRY and cls._SUFFIX in entry:
                            gloss = str(entry[cls._SUFFIX].to_list()[0])
                        cls._window.Element(Text.GLOSS_WORD.key).update(reading)
                        cls._window.Element(Text.GLOSSARY.key).update(gloss)

    @classmethod
    def _next_card(cls, deck):
        card, index = cls._load_card(deck)
        if card is not None and index is not None:
            cls._set_state_front(card)
        else:
            cls._set_state_finished()
            cls._update_deck(deck)

        return card, index

    @classmethod
    def _load_card(cls, deck):
        try:
            cards = deck[deck[cls._STATE] == 0]
            index = cards.index.tolist()[0]
            card = cards.iloc[0]
        except IndexError:
            card = None
            index = None
        return card, index

    @classmethod
    def _set_state_front(cls, card):
        cls._card_front = True

        Button.FLIP.enable(cls._window)
        for button in cls._RESPONSE_BUTTONS:
            button.disable(cls._window)

        gloss = cls._split_glossary(card)
        part = gloss[cls._CARD_PART]
        cls._window.Element(Text.WORD.key).update(card[cls._WORD])
        cls._window.Element(Text.PART.key).update(part)
        cls._window.Element(Text.DEFINITION.key).update('')
        cls._window.Element(Text.INFO.key).update('')

        source = card[cls._SOURCE]
        episode = card[cls._EPISODE]
        line_number = card[cls._LINE_NUMBER]
        sentences = cls._controller.get_sentences(source, episode, line_number)

        sentence_data = cls._controller.get_sentence_data(source, episode, line_number)
        for index, data in enumerate(sentence_data):
            if len(data) != 0 and cls._TEXT in data.columns.tolist():
                cls._sentence_data[index] = cls._order_sentences(sentences[index], data)
            else:
                cls._sentence_data[index] = pd.DataFrame([])

        cls._update_sentence_text(cls._sentence_data)

        screenshot = card[cls._SCREENSHOT]
        screenshot = cls._controller.load_screenshot(source, screenshot)
        cls._window.Element(Image.CARD.key).Update(screenshot.getvalue())

        audio_file = card[cls._AUDIO]
        cls._controller.play_audio(source, audio_file)

        Button.FLIP.enable(cls._window)

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
    def _update_sentence_text(cls, sentence_data):
        sentence_elements = [IterText.SENTENCE_ONE, IterText.SENTENCE_TWO]
        for index, sentence in enumerate(sentence_data):
            if cls._TEXT in sentence:
                words = sentence[cls._TEXT].tolist()
            else:
                words = []

            colours = []
            for word_no, word in enumerate(words):
                gloss_json = sentence[cls._CARD_GLOSS][word_no]
                colours.append(cls._text_colour_for_part_of_speech(gloss_json))
            sentence_elements[index].update(cls._window, words, colours)

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
    def _set_state_back(cls, card):
        cls._card_front = False

        gloss = cls._split_glossary(card)
        card_gloss = gloss[cls._CARD_GLOSS].replace(cls._SUBSTITUTE, cls._APOSTROPHE)
        info = gloss[cls._CARD_INFO]
        cls._window.Element(Text.DEFINITION.key).update(card_gloss)
        cls._window.Element(Text.INFO.key).update(info)

        Button.FLIP.disable(cls._window)
        for button in cls._RESPONSE_BUTTONS:
            button.enable(cls._window)

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
    def _set_state_finished(cls):
        cls._card_front = True
        cls._controller.stop_audio()
        cls._window.Element(Text.WORD.key).update(cls._REVIEWS_FINISHED)
        cls._window.Element(Text.PART.key).update('')
        cls._window.Element(Text.DEFINITION.key).update('')
        cls._window.Element(Text.INFO.key).update('')
        cls._window.Element(Text.GLOSS_WORD.key).update('')
        cls._window.Element(Text.GLOSSARY.key).update('')
        cls._window.Element(Image.CARD.key).Update(None)

        for button in list(cls._RESPONSE_BUTTONS.keys()) + cls._AUX_BUTTONS:
            button.disable(cls._window)

        IterText.SENTENCE_ONE.clear(cls._window)
        IterText.SENTENCE_TWO.clear(cls._window)

    @classmethod
    def _update_deck(cls, deck):
        for index in deck.index.tolist():
            deck.loc[index, cls._STATE] = 0
        cls._controller.update_deck(deck)


if __name__ == '__main__':
    ReviewView.show()
