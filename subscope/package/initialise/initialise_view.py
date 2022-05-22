# -*- coding: utf-8 -*-

import PySimpleGUI as sg
from enum import Enum

from subscope.package.initialise.initialise_control import InitialiseControl as ic
from subscope.package.database.database import Database as db
from subscope.package.Options import ManageOptions as mo


class Status(Enum):
    
    PACKAGES = (0, 'Setting up packages', None, 1)
    ICHIRAN = (1, 'Checking ichiran functionality', ic.setupIchiran, 0)
    DEFAULTS = (2, 'Writing default paths', ic.writePaths, 0)
    DATABASE = (3, 'Checking database', db.create_database, 0)

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
        sg.theme(mo.getSetting('themes', 'Main Theme'))
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
