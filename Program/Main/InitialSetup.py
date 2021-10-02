# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import os
import subprocess

from Program.Database import DataHandling as dh

def initialise():
    
    status = 'Setting up packages'
    
    wInitialise = [[sg.Column([[sg.Text(status, key='-INITIAL-')]], justification='centre')]]
    uInitialise = sg.Window('Initialisation', layout=wInitialise)
    
    startPath = os.getcwd().split('\\')
    startPath = startPath[:len(startPath)-2]
    settingsPath = '/'.join(startPath) + '/User Data/Settings'
    subtitlesPath = '/'.join(startPath) + '/User Data/Subtitles'
    
    # Check if the initialisation tasks are complete, and run any that aren't
    while True:
        event, values = uInitialise.Read(timeout=0)
        if event is None or event == 'Exit':
            break

        uInitialise.Element('-INITIAL-').Update('Checking ichiran functionality')
        uInitialise.Read(timeout=0)
        if 'ichiranSettings.txt' not in os.listdir(settingsPath):
            setupIchiran(settingsPath)
            
        uInitialise.Element('-INITIAL-').Update('Creating database')
        uInitialise.Read(timeout=0)
        if 'database.txt' not in os.listdir(subtitlesPath):
            dh.createDatabase(subtitlesPath)
        
        else:
            uInitialise.Close()
  
    return
            
        
def setupIchiran(settingsPath):
    # Test whether ichiran-cli has been installed properly, and can be accessed
    settingsFile = '/ichiranSettings.txt'
    ichiranSettings = settingsPath + settingsFile
    
    # Start at: 'C:/Users/'
    loc = os.getcwd().split('\\')
    loc = '/'.join(loc[0:3])
    
    output = ''
    for dirpath, subdirs, files in os.walk(loc):
        for x in subdirs:
            if x == 'local-projects':
                try:
                    path = os.path.join(dirpath, x) + '/ichiran'
                    output = subprocess.check_output('ichiran-cli -f ' + '何しての', shell=True, cwd=path)
                    
                    with open(ichiranSettings, 'w') as f:
                        f.write(path)
                        
                    break
                
                except:
                    continue
                
    if output == '':
        # TODO: prompt the user to find the quicklisp folder themselves
        print('No valid paths to ichiran')
    else:
        print('Ichiran found')
    
    return