import PySimpleGUI as sg
from enum import Enum
import os
from datetime import datetime

from subscope.nav import Nav
from subscope.retime.retime_events import RetimeEvents
from subscope.utilities.file_handling import FileHandling as fh


class RetimeView:
    _NAME = 'Retime Subtitles'
    _START = os.getcwd() + '/user/subtitles'

    def __init__(self, state):
        self._state = state
        self._window = self._create_window(self._state.files)

    def _layout(self, files):
        if files is None:
            files = []

        folder_column = [[Text.FOLDER.create()],
                         [Input.BROWSE.create(),
                          sg.FolderBrowse(initial_folder=self._START)]]

        subs_column = [[Text.SUBTITLE.create()],
                       *Checklist(files, True).create()]

        retime_column = [[Text.OFFSET.create(),
                          Input.OFFSET.create(),
                          Buttons.UPDATE.create()],
                         [Text.STATUS.create(),
                          Text.MESSAGE.create()]]

        buttons_column = [[Buttons.SELECT.create(),
                           Buttons.DESELECT.create(),
                           Buttons.BACK.create()]]

        layout = [[sg.Column(folder_column, size=(335, 60))],
                  [sg.Column(subs_column, size=(300, 300), scrollable=True),
                   sg.VSeperator(),
                   sg.Column(retime_column, size=(320, 300))],
                  [sg.Column(buttons_column)]]

        return layout

    def _create_window(self, files):
        window = sg.Window(
            title=self._NAME,
            layout=self._layout(files)
        )
        return window

    def show(self):
        event, values = self._window.Read()
        print(event)
        if event is None:
            self.close()
            event = RetimeEvents.Navigate(Nav.MAIN_MENU)

        # Browse for a folder, then update file list
        elif event.name == RetimeEvents.BrowseFiles.name:
            self._state.folder = values[Input.BROWSE.key]
            if self._state.folder:
                self._state.files = fh.get_files(self._state.folder, '.srt')

            # Update the window with the contents of the selected folder
            if self._state.files:
                self._window.write_event_value(
                    RetimeEvents.UpdateState(
                        state=self._state.copy()
                    ),
                    None
                )
                self._window.write_event_value(RetimeEvents.ReopenWindow, None)

        elif event.name == RetimeEvents.SelectAllFiles.name:
            self._select_all_files(True)

        elif event.name == RetimeEvents.DeselectAllFiles.name:
            self._select_all_files(False)

        # Adjust all selected files by the input offset
        elif event.name == RetimeEvents.RetimeSubs.name:
            offset = float(values[_Keys.OFFSET])
            selected_files = [file for file in self._state.files if values[file]]

            event = RetimeEvents.RetimeSubs(
                folder=self._state.folder,
                selected_files=selected_files,
                time_offset=offset
            )

            time_now = str(datetime.now()).split(' ')
            time_now = str(time_now[1])
            message = str(len(selected_files)) + ' file(s) updated (' + time_now[:8] + ')'
            self._window.Element(Text.MESSAGE.key).Update(value=message)

        return event

    def _select_all_files(self, select_all):
        for file in self._state.files:
            self._window.Element(file).Update(value=select_all)

    def refresh_ui(self, state):
        self._window.write_event_value(RetimeEvents.RefreshUI, state)

    def _refresh_ui(self):
        pass

    def _reopen_window(self):
        self._window.write_event_value(RetimeEvents.ReopenWindow, None)

    def close(self):
        self._window.close()


class Text(Enum):

    FOLDER = ('Select a folder containing subtitle files.', None, None)
    SUBTITLE = ('Subtitle Files', None,    None)
    OFFSET = ('Time offset (seconds):', None, None)
    STATUS = ('Status:', None, None)
    MESSAGE = ('Awaiting user selection', (20, 1), '-STATUS-')

    def __init__(self, text, size, key):
        self.text = text
        self.size = size
        self.key = key

    def create(self):
        if self.size is None:
            text = sg.Text(self.text, key=self.key)
        else:
            text = sg.Text(self.text, size=self.size, key=self.key)
        return text


class _Keys:
    OFFSET = RetimeEvents.OffsetInputChanged


class Input(Enum):

    BROWSE = ('',     (37, 1), True, RetimeEvents.BrowseFiles)
    OFFSET = ('-2.0', (10, 1), True, RetimeEvents.OffsetInputChanged)

    def __init__(self, default, size, events, key):
        self.default = default
        self.size = size
        self.events = events
        self.key = key

    def create(self):
        input_box = sg.In(default_text=self.default, size=self.size, enable_events=self.events, key=self.key)
        return input_box


# TODO: look into using a builder pattern to generalise the Buttons class
class Buttons(Enum):

    UPDATE = ('Update Files', True, RetimeEvents.RetimeSubs)
    SELECT = ('Select All', True, RetimeEvents.SelectAllFiles)
    DESELECT = ('Deselect All', True, RetimeEvents.DeselectAllFiles)
    BACK = ('Back', True, RetimeEvents.Navigate(Nav.MAIN_MENU))

    def __init__(self, text, events, key):
        self.text = text
        self.events = events
        self.key = key

    def create(self):
        button = sg.Button(self.text, enable_events=self.events, key=self.key)
        return button


class Checklist:

    def __init__(self, checklist, default):
        self.checklist = checklist
        self.default = default

    def create(self):
        checklist = [[sg.Checkbox(item, default=self.default, key=item)] for item in self.checklist]
        return checklist
