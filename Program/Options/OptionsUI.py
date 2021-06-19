# -*- coding: utf-8 -*-

# Options UI

import PySimpleGUI as sg
import pandas as pd

from Program.Options import ManageOptions as mo

def manageOptions(mainOptions):
    wOptions = sg.Window('Options', layout=mo.wOptions(mainOptions))

    # Start UI loop
    while True:
        event, values = wOptions.Read()
        if event is None or event == 'Exit' or event == 'Back':
            break
    
        if event in mainOptions:
            # TODO: sort this out
            # TODO
            # TODO
            subOptions = ['',  '',  '',  '',  '',  '',  '' ]
            
            if type(mainOptions[event]) == dict:
                optionKeys = []
                for key in mainOptions[event]:
                    optionKeys.append(key)

                for x in range(len(subOptions)):
                    if x < len(optionKeys):
                        subOptions[x] = mainOptions[event][optionKeys[x]]
                        wOptions.Element(f'-SUBHEADINGS- {x}').Update(value=optionKeys[x])
                        wOptions.Element(f'-SUBOPTIONS- {x}').Update(value=subOptions[x])
                    else:
                        subOptions[x] = ''
                        wOptions.Element(f'-SUBHEADINGS- {x}').Update(value=subOptions[x])
                        wOptions.Element(f'-SUBOPTIONS- {x}').Update(value=subOptions[x])
                
                
            elif type(mainOptions[event]) == pd.DataFrame:
                for x in range(len(subOptions)):
                    wOptions.Element(f'-SUBOPTIONS- {x}').Update(value=mainOptions[event])
                    
                    
    wOptions.close()
    
    return


'''
manageOptions(optionsPath)
'''