import copy

import PySimpleGUI as sg

from subscope.analyse.analyse_events import AnalyseEvents
from subscope.nav import Nav
from subscope.settings.settings import Settings
from subscope.utilities.file_handling import FileHandling as fh


class AnalyseView:
    _NAME = 'Analyse Subtitles'
    _START_DIR = Settings.subtitles_folder_path()
    _STATS_MSG = [
        "Total Words:" + " " * 18,
        "Total Unknown Words:" + " " * 4,
        "Comprehension (%):" + " " * 7,
        "Total Words:" + " " * 18,
        "Total Unknown Words:" + " " * 4
    ]

    def __init__(self, state):
        self._state = state
        self._window = self._create_window()

    def _layout(self):
        folder_column = [
            [
                sg.Text(
                    text="Select a folder containing subtitle files."
                )
            ],
            [
                sg.In(
                    default_text=self._state.input_folder,
                    size=(37, 1),
                    enable_events=True,
                    key=AnalyseEvents.BrowseFiles
                ),
                sg.FolderBrowse(
                    initial_folder=self._START_DIR
                )
            ]
        ]

        subs_column = [
            [
                sg.Text(
                    text="Subtitle Files"
                )
            ],
            *[[sg.Checkbox(file, default=True, key=file)] for file in self._state.files]
        ]

        statistics_column = [
            [
                sg.Button(
                    button_text="Analyse",
                    key=AnalyseEvents.AnalyseSubtitles
                )
            ],
            [sg.Text("")],
            [
                sg.Text(
                    text="Status:"
                )
            ],
            [
                sg.Text(
                    text=self._state.message or _STATUS.PRESS_BROWSE,
                    size=(30, 2),
                    key=_Keys.STATUS
                )
            ],
            [sg.Text("")],
            [
                sg.Text(
                    text="All Words",
                    font=("any", 10, "bold")
                )
            ],
            [
                sg.Text(
                    text=self._STATS_MSG[0] + str(self._state.stats.total_words),
                    key=_Keys.TOTAL_WORDS
                )
            ],
            [
                sg.Text(
                    text=self._STATS_MSG[1] + str(self._state.stats.total_unknown),
                    key=_Keys.TOTAL_UNKNOWN
                )
            ],
            [
                sg.Text(
                    text=self._STATS_MSG[2] + str(self._state.stats.comprehension),
                    key=_Keys.COMPREHENSION
                )
            ],
            [sg.Text("")],
            [
                sg.Text(
                    text="Unique Words",
                    font=("any", 10, "bold")
                )
            ],
            [
                sg.Text(
                    text=self._STATS_MSG[3] + str(self._state.stats.total_unique),
                    key=_Keys.TOTAL_UNIQUE
                )
            ],
            [
                sg.Text(
                    text=self._STATS_MSG[4] + str(self._state.stats.unique_unknown),
                    key=_Keys.UNIQUE_UNKNOWN
                )
            ],
        ]

        buttons_column = [
            [
                sg.Button(
                    button_text="Select All",
                    key=AnalyseEvents.SelectAllFiles
                ),
                sg.Button(
                    button_text="Deselect All",
                    key=AnalyseEvents.DeselectAllFiles
                ),
                sg.Button(
                    button_text="Back",
                    key=AnalyseEvents.Navigate(Nav.MAIN_MENU)
                )
            ]
        ]

        layout = [[sg.Column(folder_column, size=(335, 60))],
                  [sg.Column(
                      layout=subs_column,
                      size=(300, 350),
                      scrollable=True,
                      vertical_scroll_only=True,
                      vertical_alignment="top"
                  ),
                   sg.VSeperator(),
                   sg.Column(statistics_column)],
                  [sg.Column(buttons_column)]]

        return layout

    def _create_window(self):
        window = sg.Window(
            title=self._NAME,
            layout=self._layout()
        )
        return window

    def show(self):
        event, values = self._window.Read()
        if event is None:
            self.close()
            event = AnalyseEvents.Navigate(Nav.MAIN_MENU)

        elif event.name == AnalyseEvents.BrowseFiles.name:
            folder = values[AnalyseEvents.BrowseFiles]
            # TODO due to taking copies of state and updating in two places, the message won't update correctly
            self._update_display_message(_STATUS.PRESS_ANALYSE)
            self._browse_for_folder_and_set_files(folder)

        elif event.name == AnalyseEvents.SelectAllFiles.name:
            self._select_all_files()

        elif event.name == AnalyseEvents.DeselectAllFiles.name:
            self._deselect_all_files()

        elif event.name == AnalyseEvents.AnalyseSubtitles.name:
            state = copy.copy(self._state)
            state.selected_files = [file for file in state.files if values[file]]
            self._update_state(state)
            if state.selected_files:
                event = AnalyseEvents.AnalyseSubtitles(
                    selected_files=state.selected_files
                )

        elif event.name == AnalyseEvents.UpdateDisplayMessage.name:
            self._update_display_message(event.message)

        elif event.name == AnalyseEvents.UpdateStatsDisplay.name:
            stats = event.stats
            self._window.Element(_Keys.TOTAL_WORDS).update(
                self._STATS_MSG[0] + str(stats.total_words)
            )
            self._window.Element(_Keys.TOTAL_UNKNOWN).update(
                self._STATS_MSG[1] + str(stats.total_unknown)
            )
            self._window.Element(_Keys.COMPREHENSION).update(
                self._STATS_MSG[2] + str(stats.comprehension)
            )
            self._window.Element(_Keys.TOTAL_UNIQUE).update(
                self._STATS_MSG[3] + str(stats.total_unique)
            )
            self._window.Element(_Keys.UNIQUE_UNKNOWN).update(
                self._STATS_MSG[4] + str(stats.unique_unknown)
            )
            self._update_display_message(_STATUS.ALL_FILES_ANALYSED)

        return event

    def write_event(self, event):
        self._window.write_event_value(event, None)

    def _update_state(self, state):
        self._window.write_event_value(
            AnalyseEvents.UpdateState(
                state=state
            ),
            None
        )

    def _browse_for_folder_and_set_files(self, folder):
        state = copy.copy(self._state)
        state.input_folder = folder
        if state.input_folder:
            state.files = fh.get_files(state.input_folder, ".srt")
            self._update_state(state)
            self._window.write_event_value(AnalyseEvents.ReopenWindow, None)

    def _select_all_files(self):
        self._select_or_deselect_all_files(True)

    def _deselect_all_files(self):
        self._select_or_deselect_all_files(False)

    def _select_or_deselect_all_files(self, select_all):
        for file in self._state.files:
            self._window.Element(file).Update(value=select_all)

    def _update_display_message(self, message):
        state = copy.copy(self._state)
        state.message = message
        self._update_state(state)
        self._window.Element(_Keys.STATUS).Update(value=message)

    def close(self):
        self._window.close()


class _Keys:
    TOTAL_WORDS = "-TOTAL_WORDS-"
    TOTAL_UNKNOWN = "-TOTAL_UNKNOWN-"
    COMPREHENSION = "-COMPREHENSION-"
    TOTAL_UNIQUE = "-TOTAL_UNIQUE-"
    UNIQUE_UNKNOWN = "-UNIQUE_UNKNOWN-"
    STATUS = "-STATUS-"


class _STATUS:
    PRESS_BROWSE = "Press 'Browse' to select a location with subtitles for analysis"
    PRESS_ANALYSE = "Press 'Analyse Files' once subtitle files are selected on the left"
    UPDATING_DATABASE = "Updating the database"
    ALL_FILES_ANALYSED = "All selected files analysed"
