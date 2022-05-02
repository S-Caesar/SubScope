# -*- coding: utf-8 -*-

import PySimpleGUI as sg
from enum import Enum
import os
from datetime import datetime

from package.retime.retime_control import RetimeControl
from package.general.file_handling import FileHandling as fh

class Text(Enum):
    
    FOLDER      = ('Select a folder containing subtitle files.',  None,   None      )
    SUBTITLE    = ('Subtitle Files',                              None,   None      )
    OFFSET      = ('Time offset (seconds):',                      None,   None      )
    STATUS      = ('Status:',                                     None,   None      )
    MESSAGE     = ('Awaiting user selection',                     (20,1), '-STATUS-')
    
    def __init__(self, text, size, key):
        self.text = text
        self.size = size
        self.key = key
       
        
class Input(Enum):
    
    BROWSE      = ('',       (37,1), True, '-BROWSE-')
    OFFSET      = ('-2.0',   (10,1), True, '-OFFSET-')
    
    def __init__(self, default, size, events, key):
        self.default = default
        self.size = size
        self.events = events
        self.key = key
        
        
class Buttons(Enum):

    UPDATE      = ('Update Files',  True)
    SELECT      = ('Select All',    True)
    DESELECT    = ('Deselect All',  True)
    BACK        = ('Back',          True)
    
    def __init__(self, text, events):
        self.text = text
        self.events = events


class RetimeView:
    
    _NAME = 'Retime Subtitles'
    _START = os.getcwd() + '/user/subtitles'
    
    def _layout(self, files):

        folderColumn = [[sg.Text(Text.FOLDER.text)],
                        [sg.In(size=Input.BROWSE.size, 
                               enable_events=Input.BROWSE.events,
                               key=Input.BROWSE.key),
                         sg.FolderBrowse(initial_folder=self._START)]]
        
        subsColumn = [[sg.Text(Text.SUBTITLE.text)],
                     *[[sg.Checkbox(file,
                                    default=True,
                                    key=file)]
                       for file in files]]
        
        retimeColumn = [[sg.Text(Text.OFFSET.text),
                         sg.In(default_text=Input.OFFSET.default,
                               size=Input.OFFSET.size,
                               enable_events=Input.OFFSET.events,
                               key=Input.OFFSET.key),
                         sg.Button(Buttons.UPDATE.text,
                                   enable_events=Buttons.UPDATE.events)],
                        [sg.Text(Text.STATUS.text),
                         sg.Text(Text.MESSAGE.text,
                                 size=Text.MESSAGE.size,
                                 key=Text.MESSAGE.key)]]
        
        buttonsColumn = [[sg.Button(Buttons.SELECT.text,
                                    enable_events=Buttons.SELECT.events),
                          sg.Button(Buttons.DESELECT.text,
                                    enable_events=Buttons.DESELECT.events),
                          sg.Button(Buttons.BACK.text,
                                    enable_events=Buttons.BACK.events)]]
        
        layout = [[sg.Column(folderColumn,
                             size=(335,60))],
                  [sg.Column(subsColumn,
                             size=(300,300),
                             scrollable=True),
                   sg.VSeperator(),
                   sg.Column(retimeColumn,
                             size=(320,300))],
                  [sg.Column(buttonsColumn)]]
        
        return layout
    
    def _window(self, files=[]):
        window = sg.Window(self._NAME, layout=self._layout(files))
        return window
    
    def show(self):
        files = []
        control = RetimeControl()
        window = self._window()
        while True:
            event, values = window.Read(timeout=0)
            if event in [None, 'Back']:
                break
            
            if event == Input.BROWSE.key:
                folder = values[Input.BROWSE.key]
                files = fh.getFiles(folder, '.srt')
                
                # TODO: If subs are selected, then user browses again and
                #       selects cancel, the select/deselect buttons sometimes
                #       stop working
                if files != []:
                    # Update the window with the contents of the selected folder
                    window.Close()
                    window = self._window(files)
                    event, values = window.Read(timeout=0)
            
            switch = {Buttons.SELECT.text: True,
                      Buttons.DESELECT.text: False}
            if event in switch:
                for file in files:
                    window.Element(file).Update(value=switch[event])
            
            if event == Buttons.UPDATE.text:
                offset = float(values[Input.OFFSET.key])

                selectFiles = [file for file in files if values[file]==True]
                for file in selectFiles:
                    control.retime(folder + '/' + file, offset)
                
                timeNow = str(datetime.now()).split(' ')
                timeNow = str(timeNow[1])
                message = str(len(selectFiles)) + ' file(s) updated (' + timeNow[:8] + ')'
                window.Element(Text.MESSAGE.key).Update(value=message)
                
        window.Close()
            
if __name__ == '__main__':
    RetimeView().show()