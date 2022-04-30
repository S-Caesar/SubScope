# -*- coding: utf-8 -*-

import PySimpleGUI as sg
from enum import Enum

from Program.Subtitles import InitialSetupUI as isu
from Program.SRS import ReviewUI as ru
from Program.Processing import DeckMngmtUI as dmu
from Program.Database import ImportKnown as ik
from Program.Subtitles import AddSubsUI as asu
from Program.Subtitles import SubRetimerUI as sru
from Program.Parsing import SubsAnalysisUI as sau
from Program.Options import OptionsUI as ou

class Buttons(Enum):
    
    SETUP   = ('Inital Setup',          isu.initialSetup,   0)
    ADD     = ('Add Subtitles',         asu.addSubs,        0)
    RETIME  = ('Retime Subtitle',       sru.subRetime,      1)
    ANALYSE = ('Analyse Subtitles',     sau.analysis,       1)
    IMPORT  = ('Import Known Words',    ik.importKnown,     2)
    DECKS   = ('Manage Decks',          dmu.manageDecks,    2)
    REVIEW  = ('Review Cards',          ru.reviewCards,     3)
    OPTIONS = ('Change Settings',       ou.manageOptions,   4)
    
    def __init__(self, text, action, row):
        self.text = text
        self.action = action
        self.row = row


class MainMenu:

    def __init__(self):
        self.name = 'Main Menu'

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
        window = sg.Window(self.name, layout=self._layout, finalize=True)
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