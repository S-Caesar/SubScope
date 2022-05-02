# -*- coding: utf-8 -*-

import PySimpleGUI as sg
from enum import Enum

from package.help.help_view import HelpView as hv
from package.retime.retime_view import RetimeView as rv
from package.SRS import ReviewUI as ru
from package.Processing import DeckMngmtUI as dmu
from package.Database import ImportKnown as ik
from package.Parsing import SubsAnalysisUI as sau
from package.Options import OptionsUI as ou

class Buttons(Enum):
    
    RETIME  = ('Retime Subtitles',      rv().show,          0)
    ANALYSE = ('Analyse Subtitles',     sau.analysis,       0)
    IMPORT  = ('Import Known Words',    ik.importKnown,     1)
    DECKS   = ('Manage Decks',          dmu.manageDecks,    1)
    REVIEW  = ('Review Cards',          ru.reviewCards,     2)
    OPTIONS = ('Change Settings',       ou.manageOptions,   3)
    SETUP   = ('Help',                  hv().show,          4)
    
    def __init__(self, text, action, row):
        self.text = text
        self.action = action
        self.row = row


class MainView:

    def __init__(self):
        self._name = 'Main Menu'

    @property
    def _layout(self):
        column = []
        offset = 0
        for button in Buttons:
            if offset != button.row:
                column.append([sg.Text('='*30)])
                offset += 1
                
            try:
                column[button.row + offset].append(sg.Button(button.text))
            except:
                column.append([sg.Button(button.text)])

        layout = []
        for row in column:
            layout.append([sg.Column([row], justification='centre')]) 
          
        return layout
    
    @property
    def _window(self):
        window = sg.Window(self._name, layout=self._layout, finalize=True)
        return window
    
    def show(self):
        # Window has to be assigned, otherwise it won't close properly
        window = self._window
        while True:
            event, values = window.Read()
            if event is None:
                break
      
            for button in Buttons:
                if event == button.text:
                    window.Close()
                    button.action()
            
            # Need to close and reread the window in case the theme has changed
            window = self._window