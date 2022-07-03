from enum import Enum
import PySimpleGUI as sg


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


class IterText(Enum):
    SENTENCE_ONE = ([''] * 10, 'bold 18', f'SENTENCE_ONE', True, 'black')
    SENTENCE_TWO = ([''] * 10, 'bold 18', f'SENTENCE_TWO', True, 'black')

    def __init__(self, text, font, key, enable_events, background_colour):
        self.text = text
        self.font = font
        self.key = key
        self.enable_events = enable_events
        self.background_colour = background_colour

    def create(self):
        iter_text = [[sg.Text(text,
                              font=self.font,
                              key=f'{self.key}{index}',
                              enable_events=True,
                              background_color=self.background_colour)
                      for index, text, in enumerate(self.text)]]
        return iter_text

    def update(self, window, text, colours=None):
        if colours is None:
            colours = [None] * len(self.text)

        # TODO: centre the text within the blanks
        if len(text) < len(self.text):
            text = text + ['']*(len(self.text)-len(text))

        if len(colours) < len(self.text):
            colours = colours + [None]*(len(self.text)-len(colours))

        for index, _ in enumerate(self.text):
            window.Element(f'{self.key}{index}').update(text[index])
            window.Element(f'{self.key}{index}').update(text_color=colours[index])

    def clear(self, window):
        text = [''] * len(self.text)
        colours = [None] * len(self.text)
        self.update(window, text, colours)


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

    def disable(self, window):
        window.Element(self.text).update(disabled=True)

    def enable(self, window):
        window.Element(self.text).update(disabled=False)


class Image(Enum):
    CARD = ('IMAGE', 'black', True)

    def __init__(self, key, background_colour, visible):
        self.key = key
        self.background_colour = background_colour
        self.visible = visible

    def create(self):
        return sg.Image(key=self.key, visible=self.visible, background_color=self.background_colour)


class Combo(Enum):
    DECK_SELECTION = ('DECK_SELECTION', (15, 1), True, True)

    def __init__(self, key, size, enable_events, read_only):
        self.key = key
        self.size = size
        self.enable_events = enable_events
        self.read_only = read_only

    def create(self, options):
        return sg.Combo(options, key=self.key, enable_events=self.enable_events, readonly=self.read_only)
