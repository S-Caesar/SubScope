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
        column = []
        offset = 0
        for button in Buttons:
            if offset != button.row:
                column.append([sg.Text("="*30)])
                offset += 1

            # If a row has been created, append to it, otherwise create one
            try:
                column[button.row + offset].append(button.create())
            except IndexError:
                column.append([sg.Button(button.text)])

        layout = []
        for row in column:
            layout.append([sg.Column([row], justification="centre")])

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
            self._window.Close()

        for button in Buttons:
            if event == button.text:
                event = MainEvents.Navigate(
                    destination=button.destination
                )

        return event


class Buttons(Enum):
    RETIME = ("Retime Subtitles", Nav.RETIME, 0)
    ANALYSE = ("Analyse Subtitles", Nav.ANALYSE, 0)
    IMPORT = ("Import Known Words", Nav.IMPORT, 1)
    DECKS = ("Manage Decks", Nav.DECKS, 1)
    REVIEW = ("Review Cards", Nav.REVIEW, 2)
    OPTIONS = ("Change Settings", Nav.OPTIONS, 3)
    SETUP = ("Help", Nav.SETUP, 4)

    def __init__(self, text, destination, row):
        self.text = text
        self.destination = destination
        self.row = row

    def create(self):
        button = sg.Button(
            button_text=self.text,
        )
        return button
