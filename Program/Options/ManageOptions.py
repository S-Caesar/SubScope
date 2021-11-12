# -*- coding: utf-8 -*-

# Options functions (read in and modify settings)

import pandas as pd
import sys
import os


def readOptions(group):
    '''
    Read in the specified options file, and return is as a DataFrame
    
    group: the options file group ('paths', 'decks', 'themes')
    '''
    
    startPath = os.getcwd().split('\\')
    optionsPath = '/'.join(startPath[:-2]) + '/User Data/Settings/'
    
    # [group, file, dataType]
    groups = [['paths',     'defaultPaths.txt'],
              ['decks',     'deckSettings.txt'],
              ['themes',    'themesUI.txt'    ],
              ['formats',   'cardFormats.txt' ]]
    
    # Check whether the specified group exists, and get the entry if it does
    names = []
    for x in range(len(groups)):
        names.append(groups[x][0])
        if group in names:
            optionsFile = groups[x][1]
            break
    
    if group not in names:
        sys.exit('\nInvalid group name: ' + '\'' + group + '\'\nValid names: ' + str(names).strip('[').strip(']'))
    
    else:
        file = pd.read_csv(optionsPath + optionsFile, sep='\t')

    return file


def getSetting(group, option):
    '''
    Used to read the setting value from the DataFrame when the format is like a dictinary
    
    group: the options file group ('paths', 'decks', 'themes')\t
    option: the option heading in the file\t\n
        paths - 'Deck Folder', 'Source Folder', 'Options Folder', 'Ichiran Path'\t
        themes - 'Main Theme', 'SRS Text Colouring'
    '''
    options = readOptions(group)
    
    # Check whether the option is valid for the specified options group
    if len(options[options['Option'] == option]) == 0:
        sys.exit('\nNo option named ' + '\'' + option + '\'' + ' in group ' + '\'' + group + '\'')
        
    else:
        options = options[options['Option'] == option].reset_index(drop=True)
        setting = options['Setting'][0]

    return setting


if __name__ == '__main__':
    print(readOptions('formats'))