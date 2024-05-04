import PySimpleGUI as sg
from enum import Enum

from subscope.initialise.initialise_control import InitialiseControl as ic
from subscope.database.database import Database as db
from subscope.options.options import Options


class Status(Enum):
    
    PACKAGES = (0, 'Setting up packages', None, 1)
    DEFAULTS = (1, 'Checking settings file', ic.check_settings_file, 0)
    DATABASE = (2, 'Checking database', db.create_database, 0)

    def __init__(self, step, text, action, done):
        self.step = step
        self.text = text
        self.action = action
        self.done = done


class InitialiseView:

    _NAME = 'Initialisation'
    _TIMEOUT = 100

    @property
    def _layout(self):
        readout = []
        for status in Status:
            readout.append([sg.Checkbox(status.text,
                                        default=status.done,
                                        key=f'-INITIAL{status.step}-')])

        layout = [[sg.Column(readout)]]
        return layout
    
    @property
    def _window(self):
        sg.theme(Options.main_theme())
        window = sg.Window(self._NAME,
                           layout=self._layout,
                           disable_close=True)
        return window

    def show(self):
        window = self._window
        while True:
            event, values = window.Read(timeout=self._TIMEOUT)
            if event is None:
                break
            
            # Check if initialisation tasks are complete, and run any that aren't
            for status in Status:
                if status.done == 0:
                    if status.action is not None:
                        status.action()
                    
                    status.done = 1
                    window.Element(f'-INITIAL{status.step}-').Update(status.done)
                    window.Read(timeout=self._TIMEOUT)
                
            window.Close()
