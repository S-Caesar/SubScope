import PySimpleGUI as sg
from enum import Enum

from subscope.main_menu.main_events import MainEvents
from subscope.nav import Nav


class MainView:
    _NAME = "Main Menu"

    def __init__(self, state):
        self._state = state
        self._window = self._create_window()

    @property
    def _layout(self):
        button_width = 10
        button_height = 1
        button_text_size = 16

        title = [
            [
                sg.Text(
                    text="SubScope",
                    font="Any 18"
                )
            ]
        ]

        subtitles = [
            [
                sg.Button(
                    button_text=Buttons.RETIME.text,
                    key=Buttons.RETIME.destination,
                    size=(button_width, button_height * 3),
                    font=f"Any {button_text_size}"
                )
            ],
            [
                sg.Button(
                    button_text=Buttons.ANALYSE.text,
                    key=Buttons.ANALYSE.destination,
                    size=(button_width, button_height * 3),
                    font=f"Any {button_text_size}"
                )
            ]
        ]

        review_cards_and_settings = [
            [
                sg.Button(
                    button_text=Buttons.REVIEW.text,
                    key=Buttons.REVIEW.destination,
                    size=(button_width * 2, button_height * 5),
                    font=f"Any {button_text_size}"
                )
            ],
            [
                sg.Button(
                    button_text=Buttons.SETTINGS.text,
                    key=Buttons.SETTINGS.destination,
                    size=(button_width, button_height),
                    font=f"Any {button_text_size}"
                ),
                sg.Button(
                    button_text=Buttons.HELP.text,
                    key=Buttons.HELP.destination,
                    size=(button_width, button_height),
                    font=f"Any {button_text_size}"
                )
            ]
        ]

        manage_decks = [
            [
                sg.Button(
                    button_text=Buttons.DECKS.text,
                    key=Buttons.DECKS.destination,
                    size=(button_width, button_height * 3),
                    font=f"Any {button_text_size}"
                ),
            ],
            [
                sg.Button(
                    button_text=Buttons.IMPORT.text,
                    key=Buttons.IMPORT.destination,
                    size=(button_width, button_height * 3),
                    font=f"Any {button_text_size}"
                )
            ]
        ]

        layout = [
            [
                sg.Column(title, element_justification="centre")
            ],
            [
                sg.Column(subtitles, element_justification="centre"),
                sg.Column(review_cards_and_settings, element_justification="centre"),
                sg.Column(manage_decks, element_justification="centre"),
            ]
        ]
        layout = [[sg.Column(layout, element_justification="centre")]]
        return layout

    def _create_window(self):
        window = sg.Window(
            self._NAME,
            layout=self._layout
        )
        return window

    def show(self):
        event, values = self._window.Read()
        if event is None:
            self.close()

        for button in Buttons:
            if event == button.destination:
                event = MainEvents.Navigate(
                    destination=button.destination
                )
        return event

    def close(self):
        self._window.Close()


class Buttons(Enum):
    RETIME = ("Retime Subtitles", Nav.RETIME)
    ANALYSE = ("Analyse Subtitles", Nav.ANALYSE)
    IMPORT = ("Import Known Words", Nav.IMPORT)
    DECKS = ("Manage Decks", Nav.DECKS)
    REVIEW = ("Review Cards", Nav.REVIEW)
    SETTINGS = ("Settings", Nav.SETTINGS)
    HELP = ("Help", Nav.HELP)

    def __init__(self, text, destination):
        self.text = text
        self.destination = destination


if __name__ == "__main__":
    from subscope.main_menu.main_state import MainState
    test_state = MainState(theme=sg.theme())
    view = MainView(test_state)
    view.show()
