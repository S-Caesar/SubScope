import os
import PySimpleGUI as sg
from enum import Enum

from subscope.analyse.analyse_control import AnalyseControl
from subscope.utilities.file_handling import FileHandling as fh


class Text(Enum):

    FOLDER = ('Select a folder containing subtitle files.', None, None, None)
    SUBTITLE = ('Subtitle Files', ('any', 10, 'bold'), None, None)
    STATUS = ('Status:', ('any', 10, 'bold'), None, None)
    MESSAGE = ('', None, (30, 2), '-STATUS-')
    ALL_WORDS = ('All Words', ('any', 10, 'bold'), None, None)
    UNIQUE_WORDS = ('Unique Words', ('any', 10, 'bold'), None, None)

    def __init__(self, text, font, size, key):
        self.text = text
        self.font = font
        self.size = size
        self.key = key

    def create(self):
        if self.size is None:
            text = sg.Text(self.text, font=self.font, key=self.key)
        else:
            text = sg.Text(self.text, font=self.font, size=self.size, key=self.key)
        return text


class Input(Enum):

    BROWSE = ('', (37, 1), True, '-BROWSE-')

    def __init__(self, default, size, events, key):
        self.default = default
        self.size = size
        self.events = events
        self.key = key

    def create(self):
        input_box = sg.In(default_text=self.default, size=self.size, enable_events=self.events, key=self.key)
        return input_box


class Buttons(Enum):

    ANALYSE = ('Analyse Files', True)
    SELECT = ('Select All', True)
    DESELECT = ('Deselect All', True)
    BACK = ('Back', True)

    def __init__(self, text, events):
        self.text = text
        self.events = events

    def create(self):
        button = sg.Button(self.text, enable_events=self.events)
        return button


class Checklist:

    def __init__(self, checklist, default):
        self.checklist = checklist
        self.default = default

    def create(self):
        checklist = [[sg.Checkbox(item, default=self.default, key=item)] for item in self.checklist]
        return checklist


class AnalyseView:

    _NAME = 'Analyse Subtitles'
    _START = os.getcwd() + '/user/subtitles'
    _TIMEOUT = 100

    stats_display = [['Number:' + ' ' * 22,
                      'Unknown:' + ' ' * 20,
                      'Comprehension (%):' + ' ' * 4,
                      'Number:' + ' ' * 22,
                      'Unknown:' + ' ' * 20],
                     ['-', '-', '-', '-', '-'],
                     ['-aWORDS-', '-aUNKNOWN-', '-COMP-', '-uWORDS-', '-uUNKNOWN-']]

    def _layout(self, files):

        if files is None:
            files = []

        folder_column = [[Text.FOLDER.create()],
                         [Input.BROWSE.create(),
                          sg.FolderBrowse(initial_folder=self._START)]]

        subtitle_column = [[Text.SUBTITLE.create()],
                           *Checklist(files, True).create()]

        statistics_column = [[Buttons.ANALYSE.create()],
                             [sg.Text('')],
                             [Text.STATUS.create()],
                             [Text.MESSAGE.create()],
                             [sg.Text('')],

                             [Text.ALL_WORDS.create()],
                             *[[sg.Text(self.stats_display[0][i] + str(self.stats_display[1][i]),
                                        size=(30, 1),
                                        key=self.stats_display[2][i])]
                               for i in range(0, 3)],
                             [sg.Text('')],

                             [Text.UNIQUE_WORDS.create()],
                             *[[sg.Text(self.stats_display[0][i] + str(self.stats_display[1][i]),
                                        size=(30, 1),
                                        key=self.stats_display[2][i])]
                               for i in range(3, 5)]]

        buttons_column = [[Buttons.SELECT.create(),
                           Buttons.DESELECT.create(),
                           Buttons.BACK.create()]]

        layout = [[sg.Column(folder_column, size=(335, 60))],
                  [sg.Column(subtitle_column, size=(300, 300), scrollable=True, vertical_scroll_only=True),
                   sg.VSeperator(),
                   sg.Column(statistics_column)],
                  [sg.Column(buttons_column)]]

        return layout

    def _window(self, files=None):
        window = sg.Window(self._NAME,
                           layout=self._layout(files))
        return window

    def show(self):

        # TODO: Implement this better so it isn't just dumped at the start of the 'show' function
        completed_files = 0
        total_files = 0
        analysis_time = 0

        statuses = ['Press \'Browse\' to select a location \nwith subtitles for analysis',
                    'Press \'Analyse Files\' once subtitle \nfiles are selected on the left',
                    ('Analysing file ', completed_files, ' / ', total_files, '(Approximately ', analysis_time,
                     'minutes remaining)'),
                    'Updating the database',
                    'All selected files analysed']

        files = []
        folder = ''
        status = 0
        controller = AnalyseControl()
        window = self._window()
        while True:
            event, values = window.Read(timeout=self._TIMEOUT)
            window.Element(Text.MESSAGE.key).update(statuses[status])
            if event in [None, 'Back']:
                window.Close()
                break

            # Browse for a folder, then update file list
            if event == Input.BROWSE.key:
                folder = values[Input.BROWSE.key]
                if folder:
                    files = fh.get_files(folder, '.srt')

                # Update the window with the contents of the selected folder
                if files:
                    window.Close()
                    window = self._window(files)
                    status = 1

            # Select / deselect all files
            switch = {Buttons.SELECT.text: True,
                      Buttons.DESELECT.text: False}
            if event in switch.keys():
                for file in files:
                    window.Element(file).Update(value=switch[event])

            if event == Buttons.ANALYSE.text:
                selected_files = [file for file in files if values[file]]
                if selected_files:
                    stats = controller.analyse_subtitles(folder, selected_files)
                    if stats:
                        for x in range(len(self.stats_display[0])):
                            window.Element(self.stats_display[2][x]).update(self.stats_display[0][x] + str(stats[x]))
                    status = 4


if __name__ == '__main__':
    AnalyseView().show()
