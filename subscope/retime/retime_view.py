import copy
import PySimpleGUI as sg
from datetime import datetime

from subscope.nav import Nav
from subscope.options.options import Options
from subscope.retime.retime_events import RetimeEvents
from subscope.utilities.file_handling import FileHandling as fh


class RetimeView:
    _NAME = 'Retime Subtitles'
    _START_DIR = Options.subtitles_folder_path()

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
                    default_text=self._state.folder,
                    size=(37, 1),
                    enable_events=True,
                    key=RetimeEvents.BrowseFiles
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

        retime_column = [
            [
                sg.Text(
                    text="Time offset (seconds):"
                ),
                sg.In(
                    default_text="-2.0",
                    size=(10, 1),
                    key=RetimeEvents.OffsetInputChanged
                ),
                sg.Button(
                    button_text="Update Files",
                    key=RetimeEvents.RetimeSubs
                )
            ],
            [
                sg.Text(
                    text="Status:"
                )
            ],
            [
                sg.Text(
                    text="Awaiting user selection",
                    size=(35, 12),
                    key=_Keys.STATE
                )
            ]
        ]

        buttons_column = [
            [
                sg.Button(
                    button_text="Select All",
                    key=RetimeEvents.SelectAllFiles
                ),
                sg.Button(
                    button_text="Deselect All",
                    key=RetimeEvents.DeselectAllFiles
                ),
                sg.Button(
                    button_text="Back",
                    key=RetimeEvents.Navigate(Nav.MAIN_MENU)
                )
            ]
        ]

        layout = [
            [
                sg.Column(
                    layout=folder_column,
                    size=(335, 60)
                )
            ],
            [
                sg.Column(
                    layout=subs_column,
                    size=(300, 300),
                    scrollable=True
                ),
                sg.VSeperator(),
                sg.Column(
                    layout=retime_column,
                    size=(320, 300)
                )
            ],
            [
                sg.Column(
                    layout=buttons_column
                )
            ]
        ]

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
            event = RetimeEvents.Navigate(Nav.MAIN_MENU)

        elif event.name == RetimeEvents.BrowseFiles.name:
            folder = values[RetimeEvents.BrowseFiles]
            self._browse_for_folder_and_set_files(folder)

        elif event.name == RetimeEvents.SelectAllFiles.name:
            self._select_all_files()

        elif event.name == RetimeEvents.DeselectAllFiles.name:
            self._deselect_all_files()

        elif event.name == RetimeEvents.RetimeSubs.name:
            state = copy.copy(self._state)
            offset = float(values[RetimeEvents.OffsetInputChanged])
            state.selected_files = [file for file in state.files if values[file]]
            event = RetimeEvents.RetimeSubs(
                offset=offset,
                selected_files=state.selected_files
            )
            self._update_state(state)
            self._display_files_analysed_message(state.selected_files)

        elif event.name == RetimeEvents.UpdateDisplayMessage.name:
            self._update_display_message(event.message)

        return event

    def write_event(self, event):
        self._window.write_event_value(event, None)

    def _update_state(self, state):
        self._window.write_event_value(
            RetimeEvents.UpdateState(
                state=state
            ),
            None
        )

    def _browse_for_folder_and_set_files(self, folder):
        state = copy.copy(self._state)
        state.folder = folder
        if state.folder:
            state.files = fh.get_files(state.folder, ".srt")
            self._update_state(state)
            self._window.write_event_value(RetimeEvents.ReopenWindow, None)

    def _select_all_files(self):
        self._select_or_deselect_all_files(True)

    def _deselect_all_files(self):
        self._select_or_deselect_all_files(False)

    def _select_or_deselect_all_files(self, select_all):
        for file in self._state.files:
            self._window.Element(file).Update(value=select_all)

    def _display_files_analysed_message(self, selected_files):
        time_now = self._get_time_now()
        message = f"{len(selected_files)} file(s) updated ({time_now[:8]})"
        self._update_display_message(message)

    def _update_display_message(self, message):
        self._window.Element(_Keys.STATE).Update(value=message)

    @staticmethod
    def _get_time_now():
        time_now = str(datetime.now()).split(" ")
        time_now = str(time_now[1])
        time_now = time_now[:8]
        return time_now

    def close(self):
        self._window.close()


class _Keys:
    STATE = "-STATUS-"
    OFFSET = RetimeEvents.OffsetInputChanged
