# -*- coding: utf-8 -*-

import os
import pandas as pd
import subprocess
from enum import Enum

from Program.Options import ManageOptions as mo

class Paths(Enum):
    
    DECK    = ('Deck Folder',       'SRS/Decks',    'cwd')
    SOURCE  = ('Source Folder',     'Subtitles',    'cwd')
    OPTIONS = ('Options Folder',    'Settings',     'cwd')
    ICHIRAN = ('Ichiran Path',      '',             'C:/')
    
    def __init__(self, option, folder, start):
        self.option = option
        self.folder = folder
        self.start = start
        

class InitialiseControl:

    @staticmethod
    def writePaths(forceRebuild=False):
        '''
        Check if the 'defaultPaths.txt' file exists; create it if it doesn't
        If it does exist, check the format is correct, and overwrite if it isn't
        '''
        
        # Get the root paths for the project and user data folders
        startPath = os.getcwd().split('\\')
        root = startPath.index('SubScope')
        startPath = '/'.join(startPath[:root+1]) + '/User Data/'
        settingsFile = startPath + 'Settings/defaultPaths.txt'
        
        # If the default paths file exists, skip it unless forced to rebuild
        if os.path.isfile(settingsFile) == False or forceRebuild == True:
            headers = ['Option', 'Setting']
            defaultPaths = []
            for path in Paths:
                if path.start == 'cwd':
                    default = startPath + path.folder
                else:
                    default = path.start + path.folder
                    
                defaultPaths.append([path.option, default])
                    
            defaultPaths = pd.DataFrame(defaultPaths, columns=headers)
            defaultPaths.to_csv(settingsFile, sep='\t', index=None)

    # TODO: tidy this up next
    @staticmethod
    def setupIchiran():
        '''
        Find ichiran, test its functionality, then write the path to a .txt file
        '''
    
        optionsPath = mo.getSetting('paths', 'Options Folder')
        settingsFile = 'defaultPaths.txt'
        ichiran = 'Ichiran Path'
        
        file = pd.read_csv(optionsPath + '/' + settingsFile, sep='\t')
        
        headers = [file.columns[0], file.columns[1]]
        
        row = file[file[headers[0]] == ichiran].index.tolist()
    
        # Test whether ichiran-cli has been installed properly, and can be accessed
        if row == []:
            file = file.append(pd.DataFrame([{headers[0]: ichiran, headers[1]: 'C:/'}])).reset_index(drop=True)
            row = file[file[headers[0]] == ichiran].index.tolist()
        
        if file[headers[1]][row].values[0] == 'C:/':
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
                            break
                        
                        except:
                            continue
                    
            if output == '':
                # TODO: prompt the user to find the quicklisp folder themselves
                print('No valid paths to ichiran')
            else:
                file[headers[1]][row] = path
                file.to_csv(optionsPath + '/' + settingsFile, sep='\t', index=None)
                print('Ichiran found')
        
        else:
            path = file[headers[1]][row].values
    
        return path