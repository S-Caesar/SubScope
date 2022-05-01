# -*- coding: utf-8 -*-

import os
import pandas as pd
import subprocess
from enum import Enum


class Paths(Enum):
    
    DECK    = ('Deck Folder',       '/SRS/Decks',    ''          )
    SOURCE  = ('Source Folder',     '/Subtitles',    ''          )
    OPTIONS = ('Options Folder',    '/Settings',     ''          )
    ICHIRAN = ('Ichiran Path',      '',              'C:/Users/' )
    
    def __init__(self, option, folder, start):
        self.option = option
        self.folder = folder
        self.start = start


class InitialiseControl:

    root            = os.getcwd()
    userData        = 'User Data'
    settings        = 'Settings'
    file            = 'defaultPaths.txt'
    settingsPath    = '/'.join([root, userData, settings, file])
    userDataPath    = '/'.join([root, userData])

    headers = ['Option', 'Setting']

    @staticmethod
    def setupIchiran():
        '''
        Find ichiran, test its functionality, then update ICHIRAN with the path
        '''
        
        output = None
        target = 'local-projects'
        ichiran = 'ichiran'

        for dirpath, subdirs, files in os.walk(Paths.ICHIRAN.start):
            if target in subdirs:
                try:
                    path = os.path.join(dirpath, target) + '/' + ichiran
                    output = subprocess.check_output('ichiran-cli -f ' + '何しての', shell=True, cwd=path)
                    break
                
                except:
                    continue
                
        if output == None:
            # TODO: prompt the user to find the quicklisp folder themselves
            print('No valid paths to ichiran')
        else:
            Paths.ICHIRAN.start = path
            print('Ichiran found')

    
    @staticmethod
    def writePaths(forceRebuild=False):
        '''
        Check if the 'defaultPaths.txt' file exists; create it if it doesn't
        forceRebuild if there is an error to overwrite an existing file
        '''
        
        # If the default paths file exists, skip it unless forced to rebuild
        ic = InitialiseControl
        if os.path.isfile(ic.settingsPath) == False or forceRebuild == True:
            ic.headers
            defaultPaths = []
            for path in Paths:
                if path.start == '':
                    path.start = ic.userDataPath

                default = path.start + path.folder
                defaultPaths.append([path.option, default])
                    
            defaultPaths = pd.DataFrame(defaultPaths, columns=ic.headers)
            defaultPaths.to_csv(ic.settingsPath, sep='\t', index=None)