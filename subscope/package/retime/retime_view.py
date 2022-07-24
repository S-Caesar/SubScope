# -*- coding: utf-8 -*-

import PySimpleGUI as sg
from enum import Enum
import os
from datetime import datetime

from subscope.package.retime.retime_control import RetimeControl
from subscope.package.utilities.file_handling import FileHandling as fh


class Text(Enum):

    FOLDER   = ('Select a folder containing subtitle files.', None,    None      )
    SUBTITLE = ('Subtitle Files',                             None,    None      )
    OFFSET   = ('Time offset (seconds):',                     None,    None      )
    STATUS   = ('Status:',                                    None,    None      )
    MESSAGE  = ('Awaiting user selection',                    (20, 1), '-STATUS-')

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


class Input(Enum):

    BROWSE = ('',     (37, 1), True, '-BROWSE-')
    OFFSET = ('-2.0', (10, 1), True, '-OFFSET-')

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

    UPDATE   = ('Update Files', True)
    SELECT   = ('Select All',   True)
    DESELECT = ('Deselect All', True)
    BACK     = ('Back',         True)

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


class RetimeView:

    _NAME = 'Retime Subtitles'
    _START = os.getcwd() + '/user/subtitles'
    _TIMEOUT = 100

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

    def _window(self, files=None):
        window = sg.Window(self._NAME,
                           layout=self._layout(files))
        return window

    def show(self):
        files = []
        folder = ''
        control = RetimeControl()
        window = self._window()
        while True:
            event, values = window.Read(timeout=self._TIMEOUT)
            if event in [None, 'Back']:
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

            # Select / deselect all files
            switch = {Buttons.SELECT.text: True,
                      Buttons.DESELECT.text: False}
            if event in switch.keys():
                for file in files:
                    window.Element(file).Update(value=switch[event])

            # Adjust all selected files by the input offset
            if event == Buttons.UPDATE.text:
                offset = float(values[Input.OFFSET.key])

                selected_files = [file for file in files if values[file]]
                for file in selected_files:
                    control.retime(folder + '/' + file, offset)

                time_now = str(datetime.now()).split(' ')
                time_now = str(time_now[1])
                message = str(len(selected_files)) + ' file(s) updated (' + time_now[:8] + ')'
                window.Element(Text.MESSAGE.key).Update(value=message)

        window.Close()


if __name__ == '__main__':
    RetimeView().show()
