# -*- coding: utf-8 -*-

# UI for subtitle retiming

import PySimpleGUI as sg
import os

from Program.Subtitles import SubRetimer as sr

def subRetime():
    wSetup = sg.Window('Folder Selection', layout=sr.wSetup())
    
    # Start UI loop
    while True:
        event, values = wSetup.Read()
        if event is None or event == 'Exit':
            break
        
        if event == "-FOLDER-":
            folder = values["-FOLDER-"]
            # Get a list of files in folder
            try:
                file_list = os.listdir(folder)
            except:
                file_list = []
            
            fnames = [f for f in file_list
                      if os.path.isfile(os.path.join(folder, f))
                      and f.lower().endswith(('.srt'))]
            
    
            wSubRetimer = sg.Window('Subtitles Retimer', layout=sr.wSubRetimer(fnames))
            wSetup.Close()
            
            while True:
                event, values = wSubRetimer.Read()
                if event is None or event == 'Exit' or event == 'Back':
                    break
                
                if event == 'Select All':
                    for i in range(len(fnames)):
                        wSubRetimer.Element(f"-SUBTITLES- {i}").Update(value=True)
                        
                if event == 'Deselect All':
                    for i in range(len(fnames)):
                        wSubRetimer.Element(f"-SUBTITLES- {i}").Update(value=False)
                
                if event == 'Update Files':
                    offset = float(values['-OFFSET-'])
                    
                    # Only analyse files if they are selected
                    fnamesSelect = []
                    for i in range(len(fnames)):
                        if values[f"-SUBTITLES- {i}"] == True:
                            fnamesSelect.append(fnames[i])
                    
                    for x in range(len(fnamesSelect)):
                        sr.retime(folder, fnamesSelect[x], offset)
            
            wSubRetimer.Close()
        
    return

'''
'----------------------------------------------------------------------------'
subRetime()
'''
