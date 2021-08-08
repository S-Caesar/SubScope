# -*- coding: utf-8 -*-

# UI for subtitle retiming

import PySimpleGUI as sg
import os
from datetime import datetime

from Program.Subtitles import SubRetimer as sr
from Program.General import FileHandling as fh


def wSubRetime(fileList=[]):
    startPath = os.getcwd().split('\\')
    startPath = startPath[:len(startPath)-2]
    startPath = '/'.join(startPath) + '/User Data/Subtitles'
    
    # set up the retiming window
    folderColumn = [[sg.Text('Select a folder containing subtitle files to be retimed.')],
                    [sg.In(size=(37, 1), enable_events=True, key='-FOLDER-'),
                     sg.FolderBrowse(initial_folder=startPath)]]    
    
    subsColumn = [[sg.Text('Subtitle Files')],
                 *[[sg.Checkbox(fileList[i], default=True, key=f'-SUBTITLES_{i}-')] for i in range(len(fileList))]]
    
    retimeColumn = [[sg.Text('Time offset (seconds):'),
                     sg.In(default_text='-2.0', size=(10, 1), enable_events=True, key='-OFFSET-'),
                     sg.Button('Update Files', enable_events=True)],
                    [sg.Text('Status:'),
                     sg.Text('Awaiting user selection', size=(20,1), key='-STATUS-')]]
    
    buttonsColumn = [[sg.Button('Select All', enable_events=True),
                      sg.Button('Deselect All', enable_events=True),
                      sg.Button('Back', enable_events=True)]]
    
    
    wSubRetimer = [[sg.Column(folderColumn, size=(335,60))],
                   [sg.Column(subsColumn, size=(300,300), scrollable=True),
                    sg.VSeperator(),
                    sg.Column(retimeColumn, size=(320,300))],
                   [sg.Column(buttonsColumn)]]
                          
    return wSubRetimer


def subRetime():
    uSubRetime = sg.Window('Folder Selection', layout=wSubRetime())
    fileList = []
    
    while True:
        event, values = uSubRetime.Read()
        if event is None or event == 'Exit':
            break
        
        if event == '-FOLDER-' and values['-FOLDER-'] != '':
            folder = values['-FOLDER-']
            fileList = fh.getFiles(folder, '.srt')
            
            # Update the window with the contents of the selected folder
            uSubRetime.Close()
            uSubRetime = sg.Window('Folder Selection', layout=wSubRetime(fileList))       
            event, values = uSubRetime.Read()
            
        statusDict = {'Select All': True, 'Deselect All': False}
        if event in statusDict and fileList != []:
            fileStatus = statusDict[event]
            for i in range(len(fileList)):
                uSubRetime.Element(f'-SUBTITLES_{i}-').Update(value=fileStatus)
        
        if event == 'Update Files':
            offset = float(values['-OFFSET-'])
            
            # Only analyse files if they are selected
            x=0
            for i in range(len(fileList)):
                if values[f'-SUBTITLES_{i}-'] == True:
                    sr.retime(folder, fileList[i], offset)
                    x+=1
            
            timeNow = str(datetime.now()).split(' ')
            timeNow = str(timeNow[1])

            uSubRetime.Element('-STATUS-').Update(value = str(x) + ' file(s) updated (' + timeNow[:8] + ')')
        
        # When the window is recreated with the selected files, the back button
        # has to be pressed twice unless I put the event trigger at the end        
        if event == 'Back':
            break    
    uSubRetime.Close()
    
    return