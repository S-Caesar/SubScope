# -*- coding: utf-8 -*-

# Options functions (read in and modify settings)

import pandas as pd
import sys
import os


def readOptions(group):
    '''
    Read in the specified options file, and format accordingly
    
    group: the options file group ('paths', 'decks', 'themes')
    '''
    
    startPath = os.getcwd().split('\\')
    optionsPath = '/'.join(startPath[:-2]) + '/User Data/Settings/'
    
    # [group, file, dataType]
    groups = [['paths',     'defaultPaths.txt',      'dict' ],
              ['decks',     'deckSettings.txt',      'table'],
              ['themes',    'themesUI.txt',          'dict' ]]
    
    # Check whether the specified group exists, and get the entry if it does
    names = []
    for x in range(len(groups)):
        names.append(groups[x][0])
        if group in names:
            optionsFile = groups[x][1]
            optionsType = groups[x][2]
            break
    
    if group not in names:
        sys.exit('\nInvalid group name: ' + '\'' + group + '\'\nValid names: ' + str(names).strip('[').strip(']'))
    
    else:
        if type == 'string':
            file = open(optionsPath + optionsFile).read()
        
        elif optionsType == 'table':
            file = pd.read_csv(optionsPath + optionsFile, sep='\t')
            
        elif optionsType == 'dict':            
            rawFile = pd.read_csv(optionsPath + optionsFile, sep='\t', header=None)
            
            file = {}
            for x in range(len(rawFile)):
                file[rawFile[0][x]] = rawFile[1][x]

    return file


if __name__ == '__main__':
    print(readOptions('themes'))