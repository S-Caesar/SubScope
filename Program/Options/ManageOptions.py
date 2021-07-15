# -*- coding: utf-8 -*-

# Options functions (read in and modify settings)

import PySimpleGUI as sg
import pandas as pd

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


def readOptions(optionsPath):
    # Split up an options file and store in a dictionary
    file = open(optionsPath).read()
    options = file.split('\n\n')
    
    mainOptions = {}
    for x in range(len(options)):
        options[x] = options[x].split('\n')
        
        if options[x][1] == 'table':
            columns = options[x][2].split('\t')
            
            data = []
            if len(options[x]) > 3:
                for y in range(3, len(options[x])):
                    data.append(options[x][y].split('\t'))
                
                output = pd.DataFrame()
                output = output.append(data)
                output.columns = columns
                output = output.set_index('deckName')
                
                mainOptions[options[x][0]] = output
            
        if options[x][1] == 'dict':
            optionsDict = {}
            for y in range(2, len(options[x])):
                data = options[x][y].split('\t')
                optionsDict[data[0]] = data[1]
            
            mainOptions[options[x][0]] = optionsDict
                
    return mainOptions


'''
'----------------------------------------------------------------------------'
optionsPath = 'C:/Users/Steph/OneDrive/App/SubScope/User Data/Settings/mainOptions.txt'
mainOptions = readOptions(optionsPath)
'''