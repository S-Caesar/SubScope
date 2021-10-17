# -*- coding: utf-8 -*-

# Options functions (read in and modify settings)

import PySimpleGUI as sg
import pandas as pd
import sys
import os

def wOptions(mainOptions):

    optionHeadings = []
    for item in mainOptions:
        optionHeadings.append(item)
  
    subOptions  = ['',  '',  '',  '',  '',  '',  '' ] # empty elements to make sure the keys get updated in the menus
    
    optionsColumn = [*[[sg.Text(optionHeadings[i], enable_events=True, size=(200,1))] for i in range(len(optionHeadings))],
                    [sg.Text(' ')],
                    [sg.Button('Back')]]
    
    subHeadings = [[sg.Text(subOptions[i], size=(200,1), key=f'-SUBHEADINGS- {i}')] for i in range(len(subOptions))]
    
    subOptions = [[sg.In(default_text=subOptions[i], size=(200,1), key=f'-SUBOPTIONS- {i}')] for i in range(len(subOptions))]
    
    wOptions = [[sg.Column(optionsColumn, size=(100,300)),
                 sg.VSeparator(),
                 sg.Column(subHeadings, size=(125,300)),
                 sg.Column(subOptions, size=(400,300))]]
                          
    return wOptions


def readOptions(group):
    '''
    Read in the specified options file, and format accordingly
    
    group: the options file group ('paths', 'decks', 'ichiran', 'themes')
    '''
    
    startPath = os.getcwd().split('\\')
    optionsPath = '/'.join(startPath[:-2]) + '/User Data/Settings/'
    
    # [group, file, dataType]
    groups = [['paths',     'defaultPaths.txt',      'dict'  ],
              ['decks',     'deckSettings.txt',      'table' ],
              ['ichiran',   'ichiranSettings.txt',   'string'],
              ['themes',    'themesUI.txt',          'dict'  ]]
    
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
            rawFile = open(optionsPath + optionsFile).read().split('\n')
            
            file = {}
            for x in range(len(rawFile)):
                rawFile[x] = rawFile[x].split('\t')
                file[rawFile[x][0]] = rawFile[x][1]

    return file


def writePaths():
    # TODO: do all this properly - I hard coded it so I could mess with something else
    paths = {}
    startPath = os.getcwd().split('\\')
    
    paths['Deck Folder'] = '/'.join(startPath[:-2]) + '/User Data/SRS/Decks'
    paths['Source Folder'] = '/'.join(startPath[:-2]) + '/User Data/Subtitles'
    paths['Options Folder'] = '/'.join(startPath[:-2]) + '/User Data/Settings'
    
    file = []
    file.append('Deck Folder' + '\t' + paths['Deck Folder'])
    file.append('Source Folder\t' + paths['Source Folder'])
    file.append('Options Folder\t' + paths['Options Folder'])
    
    with open('C:/Users/Steph/OneDrive/App/SubScope/User Data/Settings/defaultPaths.txt', 'w') as f:
        for x in range(len(file)):
            f.write(file[x])

            if x != len(file)-1:
                f.write('\n')

if __name__ == '__main__':
    #optionsPath = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Settings/'
    #mainOptions = readOptions('paths')
    writePaths()