# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import os
import subprocess

from Program.Database import DataHandling as dh
from Program.Options import ManageOptions as mo

def initialise():
    '''
    Run initialisation tasks (create database, check ichiran is functional, etc.)
    '''

    # [StatusNo, Status, Action, Complete]
    status = [[0, 'Setting up packages',            None,               1],
              [1, 'Writing default paths',          mo.writePaths,      0],
              [2, 'Checking database',              dh.databaseWrapper, 0],
              [3, 'Checking ichiran functionality', setupIchiran,       0]]
    
    readout = []
    for x in range(len(status)):
        readout.append([sg.Checkbox(status[x][1], default=status[x][3], key=f'-INITIAL{x}-')])
    
    wInitialise = [[sg.Column(readout)]]
    uInitialise = sg.Window('Initialisation', layout=wInitialise, disable_close=True)

    while True:
        event, values = uInitialise.Read(timeout=0)
        if event is None or event == 'Exit':
            break
        
        # Check if the initialisation tasks are complete, and run any that aren't
        for x in range(len(status)):
            if status[x][3] == 0:
                if status[x][2] != None:
                    status[x][2]()

                status[x][3] = 1
                uInitialise.Element(f'-INITIAL{x}-').Update(status[x][3])
                uInitialise.Read(timeout=0)

        uInitialise.Close()
  
    return

        
def setupIchiran():
    '''
    Find ichiran, test its functionality, then write the path to a .txt file
    '''
    
    startPath = os.getcwd().split('\\')
    settingsPath = '/'.join(startPath[:-2]) + '/User Data/Settings'
    settingsFile = 'ichiranSettings.txt'
    
    if settingsFile not in os.listdir(settingsPath):
    
        # Test whether ichiran-cli has been installed properly, and can be accessed
        ichiranSettings = settingsPath + '/' + settingsFile
        
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