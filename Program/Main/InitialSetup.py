# -*- coding: utf-8 -*-

import os
import subprocess

def initialise():
    # Check if the initialisation tasks are complete, and run any that aren't
    startPath = os.getcwd().split('\\')
    startPath = startPath[:len(startPath)-2]
    settingsPath = '/'.join(startPath) + '/User Data/Settings'

    if 'ichiranSettings.txt' not in os.listdir(settingsPath):
        setupIchiran(settingsPath)
            
        
def setupIchiran(settingsPath):
    # Test whether ichiran-cli has been installed properly, and can be accessed
    settingsFile = '/ichiranSettings.txt'
    ichiranSettings = settingsPath + settingsFile
    
    # Start at: 'C:/Users/'
    loc = os.getcwd().split('\\')
    loc = '/'.join(loc[0:3])
    
    for dirpath, subdirs, files in os.walk(loc):
        for x in subdirs:
            if x == 'local-projects':
                try:
                    path = os.path.join(dirpath, x) + '/ichiran'
                    subprocess.check_output('ichiran-cli -f ' + '何しての', shell=True, cwd=path)
                    
                    with open(ichiranSettings, 'w') as f:
                        f.write(path)
                        
                    break
                
                except:
                    continue
                
    try:
        subprocess.check_output('ichiran-cli -f ' + '何しての', shell=True, cwd=path) 
    except:
        # TODO: prompt the user to find the quicklisp folder themselves
        print('No valid paths to ichiran')
    
    return