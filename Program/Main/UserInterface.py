# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import os

from Program.Main import InitialSetup as ins
from Program.Options import ManageOptions as mo

from Program.Subtitles import InitialSetupUI as isu
from Program.SRS import ReviewUI as ru
from Program.Processing import DeckMngmtUI as dmu
from Program.Database import ImportKnown as ik
from Program.Subtitles import AddSubsUI as asu
from Program.Subtitles import SubRetimerUI as sru
from Program.Parsing import SubsAnalysisUI as sau
from Program.Options import OptionsUI as ou


def wMainMenu(buttons):
    columns = []
    for x in buttons:
        row = []
        for y in x:
            row.append(sg.Button(y))
        columns.append([row])
        if x != buttons[-1]:
            columns.append([[sg.Text('='*30)]])
    
    mainMenu = []
    for x in columns:
        mainMenu.append([sg.Column(x, justification='centre')])
    
    return mainMenu


def mainMenu(buttons):
    ins.initialise()
    
    uMainMenu = sg.Window('Main Menu', layout=wMainMenu(buttons))
    
    # Start UI loop
    while True:
        event, values = uMainMenu.Read()
        if event is None or event == 'Exit':
            break
        
        for x in range(len(buttons)):
            if event in buttons[x]:
                for y in range(len(buttons[x])):
                    if event == buttons[x][y]:
                        uMainMenu.Hide()
                        eval(destinations[x][y])
             
            uMainMenu.UnHide()
    uMainMenu.Close()

# Read in the user settings
startPath = os.getcwd().split('\\')
startPath = startPath[:len(startPath)-2]
optionsPath = '/'.join(startPath) + '/User Data/Settings/mainOptions.txt'

mainOptions = mo.readOptions(optionsPath)
# TODO: write these back into the options file - this will do for now
mainOptions['Main Options']['Options Folder'] = '/'.join(startPath) + '/User Data/Settings'
mainOptions['Default Paths']['Deck Folder'] = '/'.join(startPath) + '/User Data/SRS/Decks'
mainOptions['Default Paths']['Source Folder'] = '/'.join(startPath) + '/User Data/Subtitles'


sg.theme(mainOptions['UI Themes']['Main Theme'])


buttons = [['Initial Setup',      'Add Subtitles'    ],
           ['Retime Subtitles',   'Analyse Subtitles'],
           ['Import Known Words', 'Manage Decks'     ],
           ['Review Cards'                           ],
           ['Change Settings'                        ]]

# NOTE: if I don't put these as strings, then the windows open when they 
#       are assigned to the list, and then won't run later
destinations = [['isu.initialSetup()',            'asu.addSubs()'               ],
                ['sru.subRetime()',               'sau.analysis(mainOptions)'   ],
                ['ik.importKnown(mainOptions)',   'dmu.manageDecks(mainOptions)'],
                ['ru.reviewCards(mainOptions)'                                  ],
                ['ou.manageOptions(mainOptions)'                                ]]

mainMenu(buttons)