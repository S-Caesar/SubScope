import PySimpleGUI as sg
from enum import Enum

from subscope.package.help.help_view import HelpView as hv
from subscope.package.retime.retime_view import RetimeView as rv
from subscope.package.parsing.analysis_view import AnalysisView as av
from subscope.package.review.review_view import ReviewView as rev
from subscope.package.known.import_known_view import ImportKnownView as ikv
from subscope.package.options.options_view import OptionsView as ov
from subscope.package.decks.decks_view import DecksView as dv


class Buttons(Enum):
    
    RETIME = ('Retime Subtitles', rv().show, 0)
    ANALYSE = ('Analyse Subtitles', av().show, 0)
    IMPORT = ('Import Known Words', ikv().show, 1)
    DECKS = ('Manage Decks', dv().show, 1)
    REVIEW = ('Review Cards', rev.show, 2)
    OPTIONS = ('Change Settings', ov().show, 3)
    SETUP = ('Help', hv().show, 4)
    
    def __init__(self, text, action, row):
        self.text = text
        self.action = action
        self.row = row

    def create(self):
        button = sg.Button(self.text)
        return button


class MainView:

    _NAME = 'Main Menu'

    @property
    def _layout(self):
        column = []
        offset = 0
        for button in Buttons:
            if offset != button.row:
                column.append([sg.Text('='*30)])
                offset += 1

            # If a row has been created, append to it, otherwise create one
            try:
                column[button.row + offset].append(button.create())
            except IndexError:
                column.append([sg.Button(button.text)])

        layout = []
        for row in column:
            layout.append([sg.Column([row], justification='centre')]) 
          
        return layout
    
    @property
    def _window(self):
        window = sg.Window(self._NAME, layout=self._layout, finalize=True)
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
