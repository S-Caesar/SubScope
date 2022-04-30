# -*- coding: utf-8 -*-

import os
import pandas as pd
import subprocess

from Program.Options import ManageOptions as mo

class InitialiseControl:
    
    def __init__(self):
        pass
    
    @staticmethod
    def writePaths():
            '''
            Check if the 'defaultPaths.txt' file exists; create it if it doesn't
            If it does exist, check the format is correct, and overwrite if it isn't
            '''
            
            startPath = os.getcwd().split('\\')
            startPath = '/'.join(startPath[:-2]) + '/User Data/'
            
            path = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Settings/'
            file = 'defaultPaths.txt'
            
            headers = ['Option', 'Setting']
            groups = pd.DataFrame([['Deck Folder',    'SRS/Decks'],
                                   ['Source Folder',  'Subtitles'],
                                   ['Options Folder', 'Settings' ],
                                   ['Ichiran Path',   ''         ]],
                                  columns=headers)
            
            # Check for the file, and if it exists, check the format is correct
            defaultPaths = []
            if os.path.isfile(path + file) == True:
                defaultPaths = pd.read_csv(path + file, sep='\t')
        
                for x in range(len(defaultPaths)):
                    # If the format of the current file is wrong, just overwrite it
                    if defaultPaths[headers[0]][x] != groups[headers[0]][x]:
                        defaultPaths = pd.DataFrame(columns=headers)
                        break
            
            # If the file doesn't exist, or is incorrect, create a new file
            if len(defaultPaths) == 0:
                defaultPaths = groups.copy()
                for x in range(len(groups)):
                    if defaultPaths[headers[0]][x] == 'Ichiran Path':
                        defaultPaths[headers[1]][x] = 'C:/'
                    else:
                        defaultPaths[headers[1]][x] = startPath + groups[headers[1]][x]
        
                defaultPaths.to_csv(path + file, sep='\t', index=None)
                        
            return
    
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