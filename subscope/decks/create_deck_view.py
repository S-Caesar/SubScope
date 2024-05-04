import PySimpleGUI as sg

from subscope.decks.decks_control import DecksControl
from subscope.decks.elements import Text, Button, InputBox


class CreateDeckView:
    _STATUS = 'STATUS'
    _SUBTITLE_SOURCE = 'SUBTITLE_SOURCE'
    _FORMAT = 'FORMAT'
    _DECK_NAME_EXISTS = 'Deck name already exists'
    _DECK_CREATED = 'Deck created!'
    _BLANK_INPUT = 'Required input is blank:\n'
    _INVALID_INPUT = 'Input must be a number:\n'

    def __init__(self):
        self._status = ''
        self._delete_status = ''
        self._selected_deck = ''

    def layout(self):
        format_list = DecksControl.formats_list()
        subtitle_list = DecksControl.subtitles_list()
        layout = [[Text.CREATE_TITLE.create()],
                  [sg.Radio(Text.EMPTY_DECK.text,
                            group_id=0,
                            default=True,
                            key=Text.EMPTY_DECK.text,
                            enable_events=True),
                   sg.Radio(Text.AUTOFILL_DECK.text,
                            group_id=0,
                            key=Text.AUTOFILL_DECK.text,
                            enable_events=True)],
                  [Text.DECK_NAME.create(),
                   InputBox.DECK_NAME.create()],
                  [Text.NEW_LIMIT.create(),
                   InputBox.NEW_LIMIT.create()],
                  [Text.REVIEW_LIMIT.create(),
                   InputBox.REVIEW_LIMIT.create()],
                  [Text.CARD_FORMAT.create(),
                   sg.Combo(format_list, key=self._FORMAT, default_value=format_list[0])],
                  [Text.SOURCE.create(),
                   sg.Combo(subtitle_list, key=self._SUBTITLE_SOURCE, disabled=True)],
                  [Text.TARGET_COMP.create(),
                   InputBox.TARGET_COMP.create()],
                  [sg.Text()],
                  [sg.Text(self._status, key=self._STATUS, size=(25, 2))],
                  [Button.CREATE_DECK.create()]]
        return layout

    def events(self, event, values, window):
        created = False
        if event in [Text.EMPTY_DECK.text, Text.AUTOFILL_DECK.text]:
            window.Element(self._SUBTITLE_SOURCE).update(disabled=(event == Text.EMPTY_DECK.text))
            window.Element(InputBox.TARGET_COMP.key).update(disabled=(event == Text.EMPTY_DECK.text))

        if event == Button.CREATE_DECK.text:
            deck_list = DecksControl.deck_list()
            deck_name = values[InputBox.DECK_NAME.key]
            new_limit = values[InputBox.NEW_LIMIT.key]
            card_format = values[self._FORMAT]
            review_limit = values[InputBox.REVIEW_LIMIT.key]
            subtitle_source = values[self._SUBTITLE_SOURCE]
            target_comprehension = values[InputBox.TARGET_COMP.key]

            if deck_name == '':
                window.Element(self._STATUS).Update(self._BLANK_INPUT + Text.DECK_NAME.text)
            elif deck_name in deck_list:
                window.Element(self._STATUS).Update(self._DECK_NAME_EXISTS)
            elif new_limit == '':
                window.Element(self._STATUS).Update(self._BLANK_INPUT + Text.NEW_LIMIT.text)
            elif review_limit == '':
                window.Element(self._STATUS).Update(self._BLANK_INPUT + Text.REVIEW_LIMIT.text)
            elif values[Text.AUTOFILL_DECK.text] and subtitle_source == '':
                window.Element(self._STATUS).Update(self._BLANK_INPUT + Text.SOURCE.text)
            elif values[Text.AUTOFILL_DECK.text] and target_comprehension == '':
                window.Element(self._STATUS).Update(self._BLANK_INPUT + Text.TARGET_COMP.text)
            else:
                try:
                    for item, error in [[new_limit, Text.NEW_LIMIT.text],
                                        [review_limit, Text.REVIEW_LIMIT.text]]:
                        try:
                            int(item)
                        except ValueError:
                            window.Element(self._STATUS).Update(self._INVALID_INPUT + error)
                            raise ValueError

                    if values[Text.AUTOFILL_DECK.text]:
                        try:
                            int(target_comprehension)
                        except ValueError:
                            window.Element(self._STATUS).Update(self._INVALID_INPUT + Text.TARGET_COMP.text)
                            raise ValueError

                    window.Element(self._STATUS).Update(self._DECK_CREATED)
                    if values[Text.EMPTY_DECK.text]:
                        subtitle_source = None
                        target_comprehension = None
                    DecksControl.create_deck(deck_name,
                                             new_limit,
                                             review_limit,
                                             card_format,
                                             subtitle_source,
                                             target_comprehension)
                    created = True

                except ValueError:
                    pass

        return created
