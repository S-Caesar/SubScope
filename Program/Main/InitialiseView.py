# -*- coding: utf-8 -*-

import PySimpleGUI as sg
from enum import Enum

from Program.Main.InitialiseControl import InitialiseControl as ic
from Program.Database import DataHandling as dh
from Program.Options import ManageOptions as mo

class Status(Enum):
    
    PACKAGES    = (0, 'Setting up packages',            None,               1)
    ICHIRAN     = (1, 'Checking ichiran functionality', ic.setupIchiran,    0)
    DEFAULTS    = (2, 'Writing default paths',          ic.writePaths,      0)
    DATABASE    = (3, 'Checking database',              dh.databaseWrapper, 0)

    def __init__(self, step, text, action, done):
        self.step = step
        self.text = text
        self.action = action
        self.done = done


class Initialise:

    def __init__(self):
        self._name = 'Initialisation'
        return

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
        sg.theme(mo.getSetting('themes', 'Main Theme'))
        window = sg.Window(self._name,
                           layout=self._layout,
                           disable_close=True)
        return window

    def show(self):
        window = self._window
        while True:
            event, values = window.Read(timeout=0)
            if event is None:
                break
            
            # Check if initialisation tasks are complete, and run any that aren't
            for status in Status:
                if status.done == 0:
                    if status.action != None:
                        status.action()
                    
                    status.done = 1
                    window.Element(f'-INITIAL{status.step}-').Update(status.done)
                    window.Read(timeout=0)
                
            window.Close()