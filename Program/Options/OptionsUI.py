# -*- coding: utf-8 -*-

# Options UI

import PySimpleGUI as sg
import pandas as pd

from Program.Options import ManageOptions as mo

def wOptions(headings):
    
    optionHeadings = []
    for item in headings:
        optionHeadings.append(item)

    # Empty elements to make sure the keys get updated in the menus
    subOptions  = ['',  '',  '',  '',  '',  '',  '' ] 
    
    optionsColumn = [*[[sg.Text(optionHeadings[x], enable_events=True, size=(10,1))] for x in range(len(optionHeadings))]]
    
    subHeadings = [[sg.Text(subOptions[x], size=(15,1), key=f'-SUBHEADINGS-{x}-')] for x in range(len(subOptions))]
    
    subOptions = [[sg.In(default_text=subOptions[x], size=(50,1), key=f'-SUBOPTIONS-{x}-')] for x in range(len(subOptions))]
    
    buttons = [[sg.Button('Back')]]
    
    wOptions = [[sg.Column(optionsColumn,vertical_alignment='top'),
                 sg.VSeparator(),
                 sg.Column(subHeadings),
                 sg.Column(subOptions)],
                [sg.Column(buttons)]]
                          
    return wOptions


def manageOptions():

    groups = pd.DataFrame([['paths',     'Default Paths',    '/defaultPaths.txt',      'dict'  ],
                           ['decks',     'Deck Settings',    '/deckSettings.txt',      'table' ],
                           ['themes',    'UI Themes',        '/themesUI.txt',          'dict'  ]],
                          columns=(['group', 'heading', 'file', 'dataType']))
    
    headings = []
    for x in range(len(groups)):
        headings.append(groups['heading'][x])
    
    optionsPath = mo.readOptions('paths')['Options Folder']

    uOptions = sg.Window('Options', layout=wOptions(headings))

    # Start UI loop
    while True:
        event, values = uOptions.Read()
        if event is None or event == 'Exit' or event == 'Back':
            break
    
        if event in headings:
            # TODO: sort this out
            # TODO
            # TODO
            subOptions = ['',  '',  '',  '',  '',  '',  '' ]
            
            headingNo = headings.index(event)
            # TODO: add headers to the txt file
            options = pd.read_csv(optionsPath + groups['file'][headingNo], sep='\t', header=None)
            print(options)
            
            if groups['dataType'][headingNo] == 'dict':
                for x in range(len(subOptions)):
                    if x < len(options):
                        uOptions.Element(f'-SUBHEADINGS-{x}-').Update(value=options[0][x])
                        uOptions.Element(f'-SUBOPTIONS-{x}-').Update(value=options[1][x])
                    
                    else:
                        uOptions.Element(f'-SUBHEADINGS-{x}-').Update(value='')
                        uOptions.Element(f'-SUBOPTIONS-{x}-').Update(value='')   
                
                event, values = uOptions.Read(timeout=0)
                        
            print(values)
                    
    uOptions.close()
    
    return


if __name__ == '__main__':
    manageOptions()